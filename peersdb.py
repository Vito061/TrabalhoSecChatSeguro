"""
Banco de dados de peers (nós) da rede P2P.
Gerencia a lista de peers conhecidos de forma thread-safe.
"""

from threading import Lock

class PeersDatabase:
    """
    Uma classe para gerenciar um banco de dados de peers (nós) em uma rede P2P.
    
    Esta classe mantém um conjunto de peers conhecidos e fornece métodos
    thread-safe para adicionar, remover e listar peers.
    """
    
    def __init__(self):
        """
        Inicializa o banco de dados de peers.
        
        Cria um conjunto vazio para armazenar os peers e um Lock para
        garantir operações thread-safe.
        """
        self.peers = set()
        self.__lock = Lock()
    
    def __str__(self):
        """
        Retorna uma representação em string do conjunto de peers.
        
        Returns:
            str: Representação em string dos peers conhecidos
        """
        return str(self.peers)
    
    def add(self, peer):
        """
        Adiciona um peer ao banco de dados de forma thread-safe.
        
        Args:
            peer: Endereço do peer no formato "IP:PORTA"
        """
        with self.__lock:
            self.peers.add(peer)
    
    def multi_add(self, peers: list):
        """
        Adiciona múltiplos peers ao banco de dados.
        
        Args:
            peers: Lista de endereços de peers
        """
        for peer in peers:
            self.add(peer)
    
    def remove(self, peer):
        """
        Remove um peer do banco de dados de forma thread-safe.
        
        Args:
            peer: Endereço do peer no formato "IP:PORTA"
        """
        with self.__lock:
            if peer in self.peers:
                self.peers.remove(peer)
    
    def clear(self):
        """Remove todos os peers do banco de dados."""
        with self.__lock:
            self.peers.clear()
    
    def get_all(self) -> set:
        """
        Retorna uma cópia do conjunto de peers.
        
        Returns:
            set: Conjunto com todos os peers conhecidos
        """
        with self.__lock:
            return self.peers.copy()
    
    def count(self) -> int:
        """
        Retorna o número de peers conhecidos.
        
        Returns:
            int: Quantidade de peers
        """
        with self.__lock:
            return len(self.peers)
    
    def exists(self, peer) -> bool:
        """
        Verifica se um peer existe no banco de dados.
        
        Args:
            peer: Endereço do peer
            
        Returns:
            bool: True se o peer existe, False caso contrário
        """
        with self.__lock:
            return peer in self.peers

# Instância global do banco de dados de peers
peersdb = PeersDatabase()