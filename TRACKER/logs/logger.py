"""
Sistema de logging para o chat P2P.
Registra todas as mensagens trocadas com timestamp.
"""

from datetime import datetime
from pathlib import Path
import os

class Logger:
    """
    Classe responsável por registrar logs das mensagens do chat.
    """
    
    def __init__(self, log_file: str = "TRACKER/logs/chat.log"):
        """
        Inicializa o logger.
        
        Args:
            log_file: Caminho para o arquivo de log
        """
        self.log_file = log_file
        
        # Garante que o diretório existe
        Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)
    
    def log(self, msg: str):
        """
        Registra uma mensagem no arquivo de log com timestamp.
        
        Args:
            msg: Mensagem a ser registrada
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(f"[{timestamp}] {msg}\n")
        except Exception as e:
            print(f"<SISTEMA>: Erro ao salvar log: {e}")
    
    def log_security_event(self, event_type: str, details: str):
        """
        Registra eventos de segurança específicos.
        
        Args:
            event_type: Tipo do evento (AUTENTICAÇÃO, INTEGRIDADE, etc.)
            details: Detalhes do evento
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(f"[{timestamp}] [SEGURANÇA:{event_type}] {details}\n")
        except Exception as e:
            print(f"<SISTEMA>: Erro ao salvar log de segurança: {e}")
    
    def clear_logs(self):
        """Limpa o arquivo de log."""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                print("<SISTEMA>: Logs limpos com sucesso.")
        except Exception as e:
            print(f"<SISTEMA>: Erro ao limpar logs: {e}")
    
    def read_logs(self, num_lines: int = None) -> list:
        """
        Lê as últimas linhas do log.
        
        Args:
            num_lines: Número de linhas a ler (None = todas)
            
        Returns:
            list: Lista com as linhas do log
        """
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            if num_lines:
                return lines[-num_lines:]
            return lines
            
        except Exception as e:
            print(f"<SISTEMA>: Erro ao ler logs: {e}")
            return []

# Instância global do logger
logger = Logger()