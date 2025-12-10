"""
Sistema de gerenciamento de salas privadas para o chat P2P.
Implementa criação, entrada e controle de acesso às salas.
"""

import hashlib
from threading import Thread
from utils import obter_hostname, socket_to_tuple

class Sala:
    """
    Representa uma sala de chat privada com senha e controle de membros.
    """
    
    def __init__(self, nome: str, porta: int, senha_hash: str, criador: str):
        """
        Inicializa uma sala de chat.
        
        Args:
            nome: Nome da sala
            porta: Porta de comunicação da sala
            senha_hash: Hash SHA-256 da senha da sala
            criador: Nome do usuário criador
        """
        self.nome = nome
        self.porta = porta
        self.ip = obter_hostname(porta)
        self.senha_hash = senha_hash
        self.criador = criador
        self.membros = []
    
    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash salvo.
        
        Args:
            senha: Senha a ser verificada
            
        Returns:
            bool: True se a senha está correta
        """
        return self.senha_hash == hashlib.sha256(senha.encode()).hexdigest()
    
    def expulsar(self, solicitante: str, usuario: str) -> str:
        """
        Expulsa um membro da sala, se quem solicitou for o criador.
        
        Args:
            solicitante: Usuário que está solicitando a expulsão
            usuario: Usuário a ser expulso
            
        Returns:
            str: Mensagem de resultado da operação
        """
        if solicitante != self.criador:
            return "<SISTEMA>: Apenas o criador da sala pode expulsar membros."
        
        if usuario not in self.membros:
            return "<SISTEMA>: Usuário não está na sala."
        
        self.membros.remove(usuario)
        return f"<SISTEMA>: Usuário {usuario} foi removido da sala {self.nome}."


class SalasDB:
    """
    Gerencia o conjunto de salas e a relação usuários ↔ salas.
    """
    
    def __init__(self):
        """Inicializa o banco de dados de salas."""
        self.salas: dict[str, Sala] = {}
        self.usuarios_sala: dict[str, str] = {}
    
    def criar_sala_com_servidor(self, nome: str, porta: int, senha: str, criador: str) -> str:
        """
        Cria uma nova sala e inicia um servidor escutando na porta especificada.
        
        Args:
            nome: Nome da sala
            porta: Porta para o servidor da sala
            senha: Senha de acesso à sala
            criador: Usuário criador da sala
            
        Returns:
            str: Mensagem de resultado
        """
        if nome in self.salas:
            return "<SISTEMA>: Sala já existe."
        
        if not senha:
            return "<SISTEMA>: É necessário definir uma senha para criar uma sala privada."
        
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        sala = Sala(nome, porta, senha_hash, criador)
        self.salas[nome] = sala
        self.usuarios_sala[criador] = nome
        sala.membros.append(criador)
        
        # Importa localmente para evitar importação circular
        import client
        from server import Server
        
        # Inicia o servidor da sala em thread separada
        servidor = Server(porta, client.cliente, criador)
        Thread(target=servidor.start, daemon=True).start()
        
        return (
            f"\n<SISTEMA>: Sala '{nome}' criada com sucesso na porta {porta}\n"
            f"<SISTEMA>: IP da sala: {sala.ip}\n"
            f"<SISTEMA>: Troca de mensagens disponível\n"
        )
    
    def entrar_sala(self, nome: str, usuario: str, senha: str = "") -> str:
        """
        Permite que um usuário entre em uma sala se a senha for correta.
        
        Args:
            nome: Nome da sala
            usuario: Nome do usuário
            senha: Senha de acesso
            
        Returns:
            str: Mensagem de resultado
        """
        if nome not in self.salas:
            return "<SISTEMA>: Sala não existe."
        
        sala = self.salas[nome]
        
        if not sala.verificar_senha(senha):
            return "<SISTEMA>: Senha incorreta."
        
        if usuario not in sala.membros:
            sala.membros.append(usuario)
            self.usuarios_sala[usuario] = nome
            return f"<SISTEMA>: Você entrou na sala {nome}."
        
        return "<SISTEMA>: Você já está na sala."
    
    def sair_sala(self, usuario: str) -> str:
        """
        Remove o usuário da sala onde ele está.
        
        Args:
            usuario: Nome do usuário
            
        Returns:
            str: Mensagem de resultado
        """
        if usuario not in self.usuarios_sala:
            return "<SISTEMA>: Você não está em nenhuma sala."
        
        nome_sala = self.usuarios_sala[usuario]
        sala = self.salas[nome_sala]
        
        if usuario in sala.membros:
            sala.membros.remove(usuario)
        
        del self.usuarios_sala[usuario]
        return f"<SISTEMA>: Você saiu da sala {nome_sala}."
    
    def listar_salas(self) -> list[str]:
        """
        Retorna uma lista com os nomes de todas as salas existentes.
        
        Returns:
            list: Lista de nomes das salas
        """
        return list(self.salas.keys())
    
    def obter_sala(self, nome: str) -> Sala:
        """
        Retorna o objeto Sala pelo nome.
        
        Args:
            nome: Nome da sala
            
        Returns:
            Sala: Objeto da sala ou None se não existir
        """
        return self.salas.get(nome)


def entrar_na_sala(e: str):
    """
    Comando para um usuário tentar entrar em uma sala existente.
    
    Args:
        e: String com o comando completo
    """
    import client
    from peersdb import peersdb
    
    partes = e.split()
    
    if len(partes) < 2:
        print("<SISTEMA>: Uso correto: /enter_room <nome> [senha]")
        return
    
    nome = partes[1]
    senha = partes[2] if len(partes) > 2 else ""
    sala = salasdb.salas.get(nome)
    
    if not sala:
        print("<SISTEMA>: Sala não encontrada.")
        return
    
    if not sala.verificar_senha(senha):
        print("<SISTEMA>: Senha incorreta.")
        return
    
    try:
        # Fecha conexões anteriores antes de entrar na nova sala
        for peer in list(peersdb.peers):
            if peer != f"{sala.ip}":
                client.cliente.disconnect(peer)
        
        # Conecta à sala
        client.cliente.connect(socket_to_tuple(f"{sala.ip}"), obter_hostname(sala.porta))
        
        # Registra o usuário na sala localmente
        from main import usuario
        
        if str(usuario) not in sala.membros:
            sala.membros.append(str(usuario))
        salasdb.usuarios_sala[str(usuario)] = nome
        
        print(f"<SISTEMA>: Você entrou na sala {nome}.")
        
    except Exception as err:
        print(f"<SISTEMA>: Erro ao conectar-se à sala: {err}")


def expulsar_usuario(e: str):
    """
    Comando para expulsar um usuário da sala, se quem executar for o criador.
    
    Args:
        e: String com o comando completo
    """
    from main import usuario
    
    partes = e.split()
    
    if len(partes) < 3:
        print("<SISTEMA>: Uso correto: /kick_peer <usuario> <sala>")
        return
    
    usuario_expulso = partes[1]
    nome_sala = partes[2]
    
    sala = salasdb.salas.get(nome_sala)
    if not sala:
        print("<SISTEMA>: Sala não encontrada.")
        return
    
    resultado = sala.expulsar(str(usuario), usuario_expulso)
    print(resultado)


# Instância global do banco de dados de salas
salasdb = SalasDB()