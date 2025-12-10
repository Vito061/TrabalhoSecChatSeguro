"""
Cliente seguro com suporte a mTLS e HMAC.
"""

from socket import *
from threading import Lock
import ssl
import json
from peersdb import peersdb
from utils import tuple_to_socket, socket_to_tuple, peers_to_str
from security import secure_manager

class ClientException(Exception):
    """Exceção para erros do cliente."""
    pass

class Connections:
    """Gerencia conexões SSL/TLS."""
    
    def __init__(self):
        self.connections: set[ssl.SSLSocket] = set()
        self.__lock = Lock()
    
    def __str__(self):
        return str(self.connections)
    
    def add(self, peer):
        with self.__lock:
            self.connections.add(peer)
    
    def remove(self, peer):
        with self.__lock:
            if peer in self.connections:
                self.connections.remove(peer)


class Client:
    """Cliente seguro com mTLS e HMAC."""
    
    def __init__(self, username: str):
        self.__connections = Connections()
        self.__concount = 0
        self.username = username
        self.ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self):
        """Cria contexto SSL/TLS com mTLS."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Carrega certificados do usuário
        cert_path = f"TRACKER/certificates/{self.username}-cert.pem"
        key_path = f"TRACKER/certificates/{self.username}-key.pem"
        ca_path = "TRACKER/certificates/ca-cert.pem"
        
        try:
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            context.load_verify_locations(cafile=ca_path)
            print(f"<SISTEMA>: Certificados carregados para {self.username}")
        except FileNotFoundError as e:
            print(f"<SISTEMA>: ERRO - Certificado não encontrado: {e}")
            print("<SISTEMA>: Execute generate_certificates.py primeiro!")
            raise
        
        return context
    
    def connect(self, addr: tuple, hostname: str):
        """Estabelece conexão segura com mTLS."""
        try:
            if addr[0] in ['127.0.0.1', '127.0.1.1']:
                raise ClientException('Conexão com localhost não permitida')
            
            # Cria socket TCP normal
            sock = socket(AF_INET, SOCK_STREAM)
            
            # Envolve com SSL/TLS
            conn = self.ssl_context.wrap_socket(sock, server_hostname=addr[0])
            conn.connect(addr)
            
            # Verifica certificado do peer
            peer_cert = conn.getpeercert()
            peer_cn = None
            for field in peer_cert.get('subject', []):
                for key, value in field:
                    if key == 'commonName':
                        peer_cn = value
                        break
            
            from utils import clear
            clear()
            print('=' * 70)
            print(f'<SISTEMA>: Conexão SEGURA estabelecida com {tuple_to_socket(addr)}')
            print(f'<SISTEMA>: Certificado do peer verificado: {peer_cn}')
            print('=' * 70)
            
            # Inicia troca de chaves Diffie-Hellman
            peer_addr = tuple_to_socket(addr)
            self._exchange_keys(conn, peer_addr)
            
            self.update_connections(conn)
            self.send_peers(conn, peers_to_str(hostname, peersdb.peers))
            peersdb.add(peer_addr)
            
            print(f'<SISTEMA>: Chave de sessão estabelecida com {peer_addr}')
            print(f'<SISTEMA>: Canal seguro pronto para troca de mensagens')
            print('=' * 70)
            
        except ssl.SSLError as e:
            print(f'<SISTEMA>: ERRO SSL - Falha na autenticação: {e}')
            print(f'<SISTEMA>: Certificado do peer pode ser inválido!')
        except ClientException as e:
            print(f'<SISTEMA>: {e}')
        except Exception as e:
            print(f'<SISTEMA>: Erro ao conectar: {e}')
            if 'conn' in locals() and conn in self.__connections.connections:
                self.__connections.remove(conn)
    
    def _exchange_keys(self, conn: ssl.SSLSocket, peer_addr: str):
        """Realiza troca de chaves Diffie-Hellman."""
        try:
            # Gera nossa chave pública DH
            my_public_key = secure_manager.initiate_key_exchange(peer_addr)
            
            # Envia nossa chave pública
            key_package = {
                "type": "DH_KEY_EXCHANGE",
                "public_key": my_public_key,
                "username": self.username
            }
            conn.sendall(json.dumps(key_package).encode('utf-8'))
            
            # Recebe chave pública do peer
            data = conn.recv(8192).decode('utf-8')
            peer_package = json.loads(data)
            
            if peer_package["type"] == "DH_KEY_EXCHANGE":
                peer_public_key = peer_package["public_key"]
                peer_username = peer_package.get("username", "unknown")
                
                # Calcula chave compartilhada
                secure_manager.complete_key_exchange(peer_addr, peer_public_key)
                
                print(f'<SISTEMA>: Troca de chaves DH concluída com {peer_username}')
            
        except Exception as e:
            print(f'<SISTEMA>: Erro na troca de chaves: {e}')
            raise
    
    def send_msg(self, msg: str):
        """Envia mensagem com HMAC para todos os peers conectados."""
        for c in list(self.__connections.connections):
            try:
                # Obtém endereço do peer
                peer_addr = tuple_to_socket(c.getpeername())
                
                # Obtém objeto de segurança para este peer
                security = secure_manager.get_security(peer_addr)
                
                if security:
                    # Empacota mensagem com HMAC
                    package = security.package_message(msg)
                    c.sendall(package.encode('utf-8'))
                else:
                    print(f'<SISTEMA>: AVISO - Sem chave segura para {peer_addr}')
                    
            except Exception as e:
                print(f'<SISTEMA>: Erro ao enviar mensagem: {e}')
                self.__connections.remove(c)
                c.close()
    
    def send_peers(self, conn: ssl.SSLSocket, peers: str):
        """Envia lista de peers."""
        conn.sendall(peers.encode('utf-8'))
    
    def update_connections(self, conn: ssl.SSLSocket):
        """Atualiza lista de conexões."""
        self.__connections.add(conn)
        self.__concount += 1
    
    @property
    def connections(self):
        """Retorna conexões e contador."""
        return self.__connections.connections, self.__concount
    
    def disconnect(self, addr_str: str):
        """Encerra conexão com um peer."""
        addr = socket_to_tuple(addr_str)
        for conn in list(self.__connections.connections):
            try:
                if conn.getpeername() == addr:
                    conn.sendall("__DISCONNECT__".encode('utf-8'))
                    conn.close()
                    self.__connections.remove(conn)
                    peersdb.remove(addr_str)
                    secure_manager.remove_peer(addr_str)
                    print(f"<SISTEMA>: Conexão encerrada com {addr_str}")
                    return
            except Exception as e:
                print(f"<SISTEMA>: Erro ao desconectar: {e}")
        print(f"<SISTEMA>: Conexão com {addr_str} não encontrada.")

# Instância global do cliente (será criada no main.py)
cliente = None