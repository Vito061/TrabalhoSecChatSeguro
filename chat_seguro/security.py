"""
Módulo de segurança para o chat P2P.
Implementa: Diffie-Hellman, HMAC, e gerenciamento de chaves.
"""

import hmac
import hashlib
import secrets
import json
from pathlib import Path

class DiffieHellman:
    """
    Implementa o protocolo Diffie-Hellman para troca de chaves.
    Permite que dois usuários estabeleçam uma chave compartilhada
    sem transmiti-la diretamente pela rede.
    """
    
    # Parâmetros do grupo Diffie-Hellman (RFC 3526 - 2048-bit MODP Group)
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
        "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
        "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
        "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
        "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
        "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
        "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16
    )
    G = 2
    
    def __init__(self):
        """Inicializa o Diffie-Hellman gerando a chave privada."""
        self.private_key = secrets.randbelow(self.P - 2) + 1
        self.public_key = pow(self.G, self.private_key, self.P)
        self.shared_secret = None
    
    def get_public_key(self) -> int:
        """Retorna a chave pública para enviar ao peer."""
        return self.public_key
    
    def compute_shared_secret(self, peer_public_key: int):
        """
        Calcula a chave compartilhada usando a chave pública do peer.
        """
        self.shared_secret = pow(peer_public_key, self.private_key, self.P)
        # Deriva uma chave de 32 bytes a partir do segredo compartilhado
        return hashlib.sha256(str(self.shared_secret).encode()).digest()
    
    def get_shared_secret(self) -> bytes:
        """Retorna a chave compartilhada derivada."""
        if self.shared_secret is None:
            raise Exception("Segredo compartilhado ainda não calculado!")
        return hashlib.sha256(str(self.shared_secret).encode()).digest()


class MessageSecurity:
    """
    Gerencia a segurança das mensagens usando HMAC.
    Garante integridade e autenticidade das mensagens.
    """
    
    def __init__(self, shared_key: bytes = None):
        """
        Inicializa com uma chave compartilhada.
        Se não fornecida, gera uma chave aleatória.
        """
        self.shared_key = shared_key or secrets.token_bytes(32)
    
    def set_shared_key(self, key: bytes):
        """Define a chave compartilhada."""
        self.shared_key = key
    
    def create_hmac(self, message: str) -> str:
        """
        Cria um HMAC para a mensagem usando SHA-256.
        Retorna o HMAC em formato hexadecimal.
        """
        h = hmac.new(
            self.shared_key,
            message.encode('utf-8'),
            hashlib.sha256
        )
        return h.hexdigest()
    
    def verify_hmac(self, message: str, received_hmac: str) -> bool:
        """
        Verifica se o HMAC recebido corresponde à mensagem.
        Retorna True se válido, False caso contrário.
        """
        expected_hmac = self.create_hmac(message)
        return hmac.compare_digest(expected_hmac, received_hmac)
    
    def package_message(self, message: str) -> str:
        """
        Empacota uma mensagem com seu HMAC.
        Formato: {"msg": "mensagem", "hmac": "hmac_value"}
        """
        mac = self.create_hmac(message)
        package = {
            "msg": message,
            "hmac": mac
        }
        return json.dumps(package)
    
    def unpackage_message(self, package: str) -> tuple:
        """
        Desempacota uma mensagem e verifica sua integridade.
        Retorna: (mensagem, válido)
        """
        try:
            data = json.loads(package)
            message = data["msg"]
            received_hmac = data["hmac"]
            
            is_valid = self.verify_hmac(message, received_hmac)
            return message, is_valid
        except (json.JSONDecodeError, KeyError):
            return None, False


class SecureConnectionManager:
    """
    Gerencia conexões seguras e suas chaves compartilhadas.
    Mapeia cada peer para sua chave de sessão.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de conexões seguras."""
        self.peer_keys = {}  # peer_addr -> MessageSecurity
        self.peer_dh = {}    # peer_addr -> DiffieHellman
    
    def initiate_key_exchange(self, peer_addr: str) -> int:
        """
        Inicia uma troca de chaves Diffie-Hellman com um peer.
        Retorna a chave pública para enviar ao peer.
        """
        dh = DiffieHellman()
        self.peer_dh[peer_addr] = dh
        return dh.get_public_key()
    
    def complete_key_exchange(self, peer_addr: str, peer_public_key: int):
        """
        Completa a troca de chaves Diffie-Hellman.
        Calcula o segredo compartilhado e cria o MessageSecurity.
        """
        if peer_addr not in self.peer_dh:
            # Se recebemos a chave pública primeiro, criamos o DH agora
            dh = DiffieHellman()
            self.peer_dh[peer_addr] = dh
        
        dh = self.peer_dh[peer_addr]
        shared_key = dh.compute_shared_secret(peer_public_key)
        
        # Cria o objeto de segurança com a chave compartilhada
        self.peer_keys[peer_addr] = MessageSecurity(shared_key)
    
    def get_security(self, peer_addr: str) -> MessageSecurity:
        """Retorna o objeto MessageSecurity para um peer específico."""
        return self.peer_keys.get(peer_addr)
    
    def has_secure_connection(self, peer_addr: str) -> bool:
        """Verifica se existe uma conexão segura estabelecida com o peer."""
        return peer_addr in self.peer_keys
    
    def remove_peer(self, peer_addr: str):
        """Remove as chaves associadas a um peer."""
        self.peer_keys.pop(peer_addr, None)
        self.peer_dh.pop(peer_addr, None)


# Instância global do gerenciador de conexões seguras
secure_manager = SecureConnectionManager()