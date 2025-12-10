"""
Servidor seguro com suporte a mTLS e HMAC.
"""

from socket import *
from threading import Thread
import ssl
import json
from peersdb import peersdb
from utils import tuple_to_socket, socket_to_tuple, obter_hostname
from security import secure_manager
from TRACKER.logs.logger import logger

class Server:
    """Servidor seguro com mTLS."""
    
    def __init__(self, port: int, client, username: str):
        self.__port = port
        self.__client = client
        self.username = username
        
        # Cria socket TCP
        self.__server = socket(AF_INET, SOCK_STREAM)
        self.__server.bind(('0.0.0.0', port))
        self.__server.listen(100)
        
        # Configura SSL/TLS
        self.ssl_context = self._create_ssl_context()
        
        self.__threads: list[Thread] = []
    
    def _create_ssl_context(self):
        """Cria contexto SSL/TLS para servidor com mTLS."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.verify_mode = ssl.CERT_REQUIRED  # mTLS: exige certificado do cliente
        
        # Carrega certificados do servidor
        cert_path = f"TRACKER/certificates/{self.username}-cert.pem"
        key_path = f"TRACKER/certificates/{self.username}-key.pem"
        ca_path = "TRACKER/certificates/ca-cert.pem"
        
        try:
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            context.load_verify_locations(cafile=ca_path)
            print(f"<SISTEMA>: Servidor SSL configurado para {self.username}")
        except FileNotFoundError as e:
            print(f"<SISTEMA>: ERRO - Certificado não encontrado: {e}")
            raise
        
        return context
    
    def start(self):
        """Inicia servidor seguro."""
        print('<SISTEMA>: Servidor SEGURO inicializado (mTLS ativo)')
        print('<SISTEMA>: Aguardando conexões...\n')
        
        try:
            while True:
                # Aceita conexão TCP
                client_sock, addr = self.__server.accept()
                
                try:
                    # Envolve com SSL/TLS
                    conn = self.ssl_context.wrap_socket(
                        client_sock,
                        server_side=True
                    )
                    
                    # Verifica certificado do cliente
                    peer_cert = conn.getpeercert()
                    peer_cn = None
                    for field in peer_cert.get('subject', []):
                        for key, value in field:
                            if key == 'commonName':
                                peer_cn = value
                                break
                    
                    print(f'<SISTEMA>: Conexão SSL aceita de {addr}')
                    print(f'<SISTEMA>: Certificado verificado: {peer_cn}')
                    
                    # Recebe primeiro pacote (DH key exchange ou peers)
                    data = conn.recv(8192).decode('utf-8')
                    
                    try:
                        # Tenta decodificar como JSON (DH key exchange)
                        package = json.loads(data)
                        if package.get("type") == "DH_KEY_EXCHANGE":
                            self._handle_key_exchange(conn, addr, package)
                    except json.JSONDecodeError:
                        # É uma lista de peers (formato antigo)
                        self._handle_peers(data)
                    
                    # Cria thread para gerenciar comunicação
                    thread = Thread(target=self.handle_peer, args=(conn, addr))
                    self.__threads.append(thread)
                    thread.start()
                    
                except ssl.SSLError as e:
                    print(f'<SISTEMA>: ERRO SSL - Autenticação falhou: {e}')
                    print(f'<SISTEMA>: Certificado de {addr} pode ser inválido!')
                    client_sock.close()
                    
        except Exception as e:
            print(f'<SISTEMA>: Erro no servidor: {e}')
        finally:
            self.finish()
    
    def _handle_key_exchange(self, conn: ssl.SSLSocket, addr: tuple, package: dict):
        """Processa troca de chaves Diffie-Hellman."""
        try:
            peer_public_key = package["public_key"]
            peer_username = package.get("username", "unknown")
            peer_addr = tuple_to_socket(addr)
            
            # Gera nossa chave pública e calcula segredo compartilhado
            my_public_key = secure_manager.initiate_key_exchange(peer_addr)
            secure_manager.complete_key_exchange(peer_addr, peer_public_key)
            
            # Envia nossa chave pública de volta
            response = {
                "type": "DH_KEY_EXCHANGE",
                "public_key": my_public_key,
                "username": self.username
            }
            conn.sendall(json.dumps(response).encode('utf-8'))
            
            print(f'<SISTEMA>: Chave de sessão estabelecida com {peer_username}')
            
        except Exception as e:
            print(f'<SISTEMA>: Erro na troca de chaves: {e}')
    
    def _handle_peers(self, data: str):
        """Processa lista de peers recebida."""
        for p in data.split():
            if p != obter_hostname(self.__port) and p not in peersdb.peers:
                import client
                if client.cliente:
                    client.cliente.connect(socket_to_tuple(p), obter_hostname(self.__port))
                    peersdb.add(p)
    
    def handle_peer(self, conn: ssl.SSLSocket, addr: tuple):
        """Gerencia comunicação com peer conectado."""
        #peer_addr = tuple_to_socket(addr)
        
        try:
            while True:
                data = conn.recv(8192)
                if not data:
                    break
                
                msg_data = data.decode('utf-8')
                
                # Verifica mensagem de desconexão
                if msg_data == "__DISCONNECT__":
                    print(f"<SISTEMA>: Peer {addr} encerrou a conexão")
                    break
                
                # Verifica se é uma mensagem com HMAC
                #security = secure_manager.get_security(peer_addr)
                security = secure_manager.get_security(conn)
                
                if security:
                    try:
                        # Desempacota e verifica integridade
                        message, is_valid = security.unpackage_message(msg_data)

                        if is_valid:
                            print(f'{message}')
                            logger.log(message)
                        else:
                            print(f'\n{"!" * 70}')
                            print(f'<SISTEMA>:   ALERTA DE SEGURANÇA ')
                            print(f'<SISTEMA>: Mensagem com INTEGRIDADE VIOLADA!')
                            print(f'<SISTEMA>: Origem: {peer_addr}')
                            print(f'<SISTEMA>: A mensagem pode ter sido ADULTERADA!')
                            print(f'{"!" * 70}\n')
                            logger.log(f"[INTEGRIDADE VIOLADA] de {peer_addr}")
                    except:
                        # Não é uma mensagem empacotada, exibe diretamente
                        print(f'{msg_data}')
                        logger.log(msg_data)
                else:
                    # Sem chave de sessão ainda, exibe mensagem
                    print(f'{msg_data}')
                    
        except Exception as e:
            print(f'<SISTEMA>: Erro ao processar mensagem de {addr}: {e}')
        finally:
            conn.close()
            peersdb.remove(peer_addr)
            secure_manager.remove_peer(peer_addr)
    
    def finish(self):
        """Finaliza servidor."""
        self.__server.close()
        for thread in self.__threads:
            thread.join()