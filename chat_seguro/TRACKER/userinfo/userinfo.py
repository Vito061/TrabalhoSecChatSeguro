"""
Módulo de gerenciamento de usuários.
Implementa cadastro, login e criptografia de senhas.
"""

import json
import os
import hashlib
import platform
from pathlib import Path

def clear():
    """Limpa a tela do terminal."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def criptografar(senha: str) -> str:
    """
    Criptografa uma senha usando o algoritmo SHA-256.
    Retorna a senha criptografada em formato hexadecimal.
    """
    hash_object = hashlib.sha256()
    hash_object.update(senha.encode('utf-8'))
    return hash_object.hexdigest()

class UserException(Exception):
    """
    Exceção personalizada para erros relacionados ao usuário.
    
    Esta exceção é levantada quando ocorre um erro específico relacionado
    às operações do usuário, como senha incorreta ou senha não confirmada.
    """
    pass

class User:
    """
    Classe responsável por gerenciar as informações e operações do usuário.
    
    Esta classe lida com o cadastro (signin) e login do usuário, além de
    armazenar as credenciais em um arquivo JSON.
    """
    
    def __init__(self):
        """
        Inicializa o usuário. Se o arquivo de credenciais existir, carrega
        as informações. Caso contrário, inicia o processo de cadastro (signin).
        """
        self.__name = ''
        self.__password = ''
        
        # Garante que o diretório existe
        Path('TRACKER/userinfo').mkdir(parents=True, exist_ok=True)
        
        if os.path.exists('TRACKER/userinfo/user.json'):
            with open('TRACKER/userinfo/user.json', 'r') as file:
                credentials = json.load(file)
            self.__name = credentials['username']
            self.__password = credentials['password']
        else:
            clear()
            print('=' * 70)
            print('           CHAT P2P SEGURO - PRIMEIRO ACESSO')
            print('=' * 70)
            print('\n<SISTEMA>: Credenciais de login não encontradas.')
            print('<SISTEMA>: Cadastre um novo usuário.\n')
            self.signin()
    
    def __str__(self) -> str:
        """Retorna o nome do usuário."""
        return self.__name
    
    def signin(self):
        """
        Realiza o cadastro de um novo usuário.
        
        O usuário é solicitado a fornecer um nome de usuário e uma senha.
        A senha é confirmada e, se válida, criptografada e armazenada junto
        com o nome do usuário em um arquivo JSON.
        """
        self.__name = input('<SISTEMA>: Nome do usuário: ')
        
        while True:
            try:
                self.__password = input('<SISTEMA>: Senha do usuário: ')
                confirm = input('<SISTEMA>: Confirme a senha do usuário: ')
                
                if self.__password != confirm:
                    raise UserException('Senha não confirmada.')
                
                if len(self.__password) < 4:
                    raise UserException('Senha muito curta (mínimo 4 caracteres).')
                
                print('\n<SISTEMA>:  Cadastro realizado com sucesso!')
                print('<SISTEMA>: Pressione ENTER para continuar...')
                input()
                break
                
            except UserException as e:
                print(f'<SISTEMA>:  {e}')
        
        # Criptografa a senha antes de salvar
        self.__password = criptografar(self.__password)
        
        credentials = {
            'username': self.__name,
            'password': self.__password
        }
        
        # Garante que o diretório existe
        Path('TRACKER/userinfo').mkdir(parents=True, exist_ok=True)
        
        with open('TRACKER/userinfo/user.json', 'w') as file:
            json.dump(credentials, file, indent=2)
    
    def login(self):
        """
        Realiza o login do usuário.
        
        O usuário é solicitado a fornecer a senha. Se a senha estiver correta,
        o login é bem-sucedido. Caso contrário, uma exceção é levantada.
        """
        while True:
            try:
                clear()
                print('=' * 70)
                print('           CHAT P2P SEGURO - AUTENTICAÇÃO')
                print('=' * 70)
                print(f'\n<SISTEMA>: Bem-vindo(a), {self.__name}!')
                
                password = input('<SISTEMA>: Digite sua senha: ')
                password_hash = criptografar(password)
                
                if password_hash != self.__password:
                    raise UserException('Senha incorreta.')
                
                print('\n<SISTEMA>:  Autenticação bem-sucedida!')
                print('<SISTEMA>: Pressione ENTER para continuar...')
                input()
                break
                
            except UserException as e:
                print(f'\n<SISTEMA>:  {e}')
                print('<SISTEMA>: Tente novamente...')
                input()