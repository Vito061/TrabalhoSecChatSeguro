"""
Aplicação principal do Chat P2P Seguro.
Implementa: mTLS, Diffie-Hellman, HMAC
"""

from threading import Thread
from server import Server
from client import Client
import client as client_module
from utils import obter_hostname, clear, socket_to_tuple, mostrar_comandos
from peersdb import peersdb
from TRACKER.salasdb import salasdb, entrar_na_sala
from TRACKER.userinfo.userinfo import User
from TRACKER.logs.logger import logger
from security import secure_manager
import os

def verificar_certificados(username: str) -> bool:
    """Verifica se os certificados do usuário existem."""
    cert_path = f"TRACKER/certificates/{username}-cert.pem"
    key_path = f"TRACKER/certificates/{username}-key.pem"
    ca_path = "TRACKER/certificates/ca-cert.pem"
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("\n" + "=" * 70)
        print("<SISTEMA>:   CERTIFICADOS NÃO ENCONTRADOS ")
        print("=" * 70)
        print(f"<SISTEMA>: Usuário: {username}")
        print(f"<SISTEMA>: Certificado esperado: {cert_path}")
        print(f"<SISTEMA>: Chave esperada: {key_path}")
        print("\n<SISTEMA>: AÇÃO NECESSÁRIA:")
        print("<SISTEMA>: 1. Execute: python generate_certificates.py")
        print(f"<SISTEMA>: 2. Gere certificado para '{username}'")
        print(f"<SISTEMA>: 3. Reinicie a aplicação")
        print("=" * 70)
        return False
    
    if not os.path.exists(ca_path):
        print("\n" + "=" * 70)
        print("<SISTEMA>:   CA (Certificate Authority) NÃO ENCONTRADA ")
        print("=" * 70)
        print("<SISTEMA>: Execute: python generate_certificates.py")
        print("<SISTEMA>: A CA será gerada automaticamente")
        print("=" * 70)
        return False
    
    return True

def mostrar_info_seguranca():
    """Exibe informações sobre as funcionalidades de segurança."""
    print("\n" + "=" * 70)
    print("CHAT P2P SEGURO - FUNCIONALIDADES IMPLEMENTADAS")
    print("=" * 70)
    print("\n SEGURANÇA DA INFORMAÇÃO:")
    print("  ✓ mTLS (mutual TLS) - Autenticação mútua cliente/servidor")
    print("  ✓ Certificados Digitais X.509 - Identidade verificada")
    print("  ✓ Diffie-Hellman - Troca segura de chaves de sessão")
    print("  ✓ HMAC-SHA256 - Garantia de integridade das mensagens")
    print("  ✓ SSL/TLS - Confidencialidade do canal de comunicação")
    print("\n PROPRIEDADES GARANTIDAS:")
    print("  • CONFIDENCIALIDADE: Mensagens criptografadas (verificável no Wireshark)")
    print("  • AUTENTICIDADE: Certificados validados por CA")
    print("  • INTEGRIDADE: HMAC detecta adulterações")
    print("=" * 70 + "\n")

# Inicialização
clear()
print("=" * 70)
print("           CHAT P2P SEGURO - INICIALIZAÇÃO")
print("=" * 70)

# Login do usuário
usuario = User()
usuario.login()

# Verifica certificados
if not verificar_certificados(str(usuario)):
    print("\n<SISTEMA>: Encerrando aplicação...")
    exit(1)

# Solicita porta
PORTA = int(input('<SISTEMA>: Digite a porta fixa de comunicação: '))

# Inicializa cliente e servidor seguros
clear()
mostrar_info_seguranca()

print("<SISTEMA>: Inicializando componentes seguros...")
cliente = Client(str(usuario))
# Atualiza a instância global no módulo client
client_module.cliente = cliente

servidor = Server(PORTA, cliente, str(usuario))
Thread(target=servidor.start, daemon=True).start()

# Comandos disponíveis
comandos = {
    '/connect': lambda e: cliente.connect(
        socket_to_tuple(e.split()[1]), 
        obter_hostname(PORTA)
    ),
    '/peers': lambda e: print(f"\n<SISTEMA>: Peers conhecidos:\n{peersdb.peers}\n"),
    '/connections': lambda e: print(
        f"\n<SISTEMA>: Conexões ativas: {cliente.connections[1]}\n"
    ),
    '/secure_status': lambda e: (
        print("\n<SISTEMA>: Conexões seguras estabelecidas:")
        if secure_manager.peer_keys
        else print("\n<SISTEMA>: Nenhuma conexão segura estabelecida ainda.\n"),
        [print(f"  • {peer}") for peer in secure_manager.peer_keys.keys()] if secure_manager.peer_keys else None,
        print()
    ),
    '/resignin': lambda e: usuario.signin(),
    '/create_room': lambda e: print(
        "<SISTEMA>: Uso: /create_room <nome> <porta> <senha>"
        if len(e.split()) < 4
        else salasdb.criar_sala_com_servidor(
            nome=e.split()[1],
            porta=int(e.split()[2]),
            senha=e.split()[3],
            criador=str(usuario)
        )
    ),
    '/disconnect': lambda e: cliente.disconnect(e.split()[1]),
    '/enter_room': lambda e: entrar_na_sala(e),
    '/clear': lambda e: (clear(), mostrar_info_seguranca()),
    '/menu': lambda e: mostrar_comandos(),
    '/security_info': lambda e: mostrar_info_seguranca()
}

mostrar_comandos()
print("\n<SISTEMA>: Sistema pronto! Digite /security_info para ver detalhes de segurança.\n")

# Loop principal
if __name__ == '__main__':
    while True:
        try:
            e = input()
            
            if e == '':
                continue
            
            if e[0] == '/':
                try:
                    comando = e.split()[0]
                    if comando in comandos:
                        comandos[comando](e)
                    else:
                        print(f'<SISTEMA>: Comando desconhecido: {comando}')
                        print('<SISTEMA>: Digite /menu para ver comandos disponíveis')
                except IndexError:
                    print('<SISTEMA>: Comando incompleto. Digite /menu para ajuda')
                except Exception as err:
                    print(f'<SISTEMA>: Erro ao executar comando: {err}')
            else:
                # Envia mensagem
                nome_sala = salasdb.usuarios_sala.get(str(usuario), None)
                if nome_sala:
                    msg = f'[{nome_sala}] <{usuario}>: {e}'
                else:
                    msg = f'<{usuario}>: {e}'
                
                cliente.send_msg(msg)
                logger.log(msg)
                
        except KeyboardInterrupt:
            print("\n\n<SISTEMA>: Encerrando aplicação...")
            break
        except Exception as err:
            print(f'<SISTEMA>: Erro: {err}')