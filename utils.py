from socket import *
import platform
import subprocess
import os

def obter_hostname(port: int) -> str:
    """
    Obtém o endereço IP do host local e o combina com a porta fornecida.
    """
    if platform.system() == 'Linux': 
        hostname = get_local_ip_linux()
    elif platform.system() == 'Windows': 
        hostname = gethostbyname(gethostname())
    else:
        hostname = gethostbyname(gethostname())
    return hostname + f':{port}'

def tuple_to_socket(addr: tuple) -> str:
    """Converte tupla (IP, porta) em string 'IP:porta'."""
    return f'{addr[0]}:{addr[1]}'

def socket_to_tuple(s: str) -> tuple:
    """Converte string 'IP:porta' em tupla (IP, porta)."""
    aux = s.split(':')
    addr = (aux[0], int(aux[1]))
    return addr

def peers_to_str(hostname: str, peers: set) -> str:
    """Converte conjunto de peers em string."""
    r = hostname
    for p in peers: 
        r += ' ' + p
    return r

def get_local_ip_linux() -> str:
    """Obtém o endereço IP local em sistemas Linux."""
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "inet " in line and "127.0.0.1" not in line:
                    return line.split()[1].split('/')[0]
        return "127.0.0.1"
    except Exception as e:
        print(f"<SISTEMA>: Erro ao obter o IP local: {e}")
        return "127.0.0.1"

def mostrar_comandos():
    """Exibe todos os comandos disponíveis no chat."""
    print("\n" + "=" * 70)
    print("COMANDOS DISPONÍVEIS - CHAT P2P SEGURO")
    print("=" * 70)
    print("\nCONEXÃO:")
    print("  /connect <IP:PORTA>           → Conecta a um peer (com mTLS)")
    print("  /disconnect <IP:PORTA>        → Desconecta de um peer")
    print("  /peers                        → Lista peers conhecidos")
    print("  /connections                  → Lista conexões ativas")
    print("\nSEGURANÇA:")
    print("  /secure_status                → Status das conexões seguras (DH+HMAC)")
    print("  /security_info                → Informações sobre segurança implementada")
    print("\nSALAS:")
    print("  /create_room <nome> <porta> <senha>  → Cria sala privada")
    print("  /enter_room <nome> [senha]           → Entra em uma sala")
    print("\nUSUÁRIO:")
    print("  /resignin                     → Recadastrar usuário")
    print("\nSISTEMA:")
    print("  /clear                        → Limpa a tela")
    print("  /menu                         → Exibe este menu")
    print("=" * 70)
    print("\nDICA: Todas as mensagens são protegidas com HMAC-SHA256!")
    print("=" * 70 + "\n")

def clear():
    """Limpa a tela e exibe o cabeçalho."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print('=' * 70)
    print('                    CHAT P2P SEGURO')
    print('                  mTLS + DH + HMAC-SHA256')
    print('=' * 70)
    print('                                             Digite /menu para ajuda\n')