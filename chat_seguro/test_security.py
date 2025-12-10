#!/usr/bin/env python3
"""
Script de teste para validar as funcionalidades de segurança.
Testa: HMAC, Diffie-Hellman, e integração básica.
"""

import sys
import hashlib
import hmac as hmac_lib
from security import DiffieHellman, MessageSecurity, SecureConnectionManager

def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_diffie_hellman():
    """Testa a troca de chaves Diffie-Hellman."""
    print_header("TESTE 1: DIFFIE-HELLMAN KEY EXCHANGE")
    
    print("\n1. Criando instâncias para Alice e Bob...")
    alice_dh = DiffieHellman()
    bob_dh = DiffieHellman()
    
    print(f"Alice - Chave privada gerada (não exibida por segurança)")
    print(f"Alice - Chave pública: {alice_dh.get_public_key()}")
    print(f"Bob   - Chave privada gerada (não exibida por segurança)")
    print(f"Bob   - Chave pública: {bob_dh.get_public_key()}")
    
    print("\n2. Trocando chaves públicas...")
    alice_public = alice_dh.get_public_key()
    bob_public = bob_dh.get_public_key()
    
    print("\n3. Calculando segredos compartilhados...")
    alice_shared = alice_dh.compute_shared_secret(bob_public)
    bob_shared = bob_dh.compute_shared_secret(alice_public)
    
    print(f"Alice calculou: {alice_shared.hex()[:32]}...")
    print(f"Bob calculou:   {bob_shared.hex()[:32]}...")
    
    print("\n4. Verificando se os segredos são iguais...")
    if alice_shared == bob_shared:
        print("SUCESSO: Segredos compartilhados são IGUAIS!")
        print(f"Tamanho da chave: {len(alice_shared) * 8} bits")
        return True
    else:
        print("FALHA: Segredos diferentes!")
        return False

def test_hmac_integrity():
    """Testa a verificação de integridade com HMAC."""
    print_header("TESTE 2: HMAC - INTEGRIDADE DE MENSAGENS")
    
    # Simula chave compartilhada
    shared_key = b"chave_secreta_compartilhada_32B!"
    
    print("\n1. Criando instância de MessageSecurity...")
    security = MessageSecurity(shared_key)
    print(f"Chave compartilhada configurada")
    
    print("\n2. Testando mensagem válida...")
    msg1 = "Olá Bob! Esta mensagem tem integridade."
    hmac1 = security.create_hmac(msg1)
    print(f"Mensagem: '{msg1}'")
    print(f"HMAC: {hmac1[:32]}...")
    
    is_valid = security.verify_hmac(msg1, hmac1)
    if is_valid:
        print("HMAC verificado: Mensagem ÍNTEGRA")
    else:
        print("HMAC inválido!")
        return False
    
    print("\n3. Testando mensagem adulterada...")
    msg2_adulterada = "Olá Bob! Esta mensagem FOI ALTERADA."
    is_valid_adulterada = security.verify_hmac(msg2_adulterada, hmac1)
    
    if not is_valid_adulterada:
        print(f"Mensagem adulterada: '{msg2_adulterada}'")
        print(f"HMAC original usado: {hmac1[:32]}...")
        print("SUCESSO: Adulteração DETECTADA!")
    else:
        print("FALHA: Adulteração NÃO detectada!")
        return False
    
    print("\n4. Testando empacotamento de mensagem...")
    package = security.package_message(msg1)
    print(f"Pacote JSON: {package[:80]}...")
    
    unpacked_msg, is_valid_unpacked = security.unpackage_message(package)
    if is_valid_unpacked and unpacked_msg == msg1:
        print("Mensagem desempacotada e verificada com sucesso!")
        return True
    else:
        print("Falha ao desempacotar/verificar!")
        return False

def test_secure_connection_manager():
    """Testa o gerenciador de conexões seguras."""
    print_header("TESTE 3: SECURE CONNECTION MANAGER")
    
    print("\n1. Criando gerenciador...")
    manager = SecureConnectionManager()
    print("SecureConnectionManager criado")
    
    print("\n2. Simulando conexão com peer 192.168.1.100:5001...")
    peer_addr = "192.168.1.100:5001"
    
    print("a) Iniciando troca de chaves...")
    my_public_key = manager.initiate_key_exchange(peer_addr)
    print(f"Minha chave pública: {my_public_key}")
    
    print("b) Simulando recebimento de chave pública do peer...")
    # Simula DH do peer
    peer_dh = DiffieHellman()
    peer_public_key = peer_dh.get_public_key()
    print(f"Chave pública do peer: {peer_public_key}")
    
    print("c) Completando troca de chaves...")
    manager.complete_key_exchange(peer_addr, peer_public_key)
    print("Troca de chaves concluída!")
    
    print("\n3. Verificando conexão segura...")
    if manager.has_secure_connection(peer_addr):
        print(f"Conexão segura estabelecida com {peer_addr}")
    else:
        print(f"Falha ao estabelecer conexão segura")
        return False
    
    print("\n4. Testando envio de mensagem segura...")
    security = manager.get_security(peer_addr)
    if security:
        msg = "Teste de mensagem com HMAC"
        package = security.package_message(msg)
        unpacked, valid = security.unpackage_message(package)
        
        if valid and unpacked == msg:
            print(f"Mensagem enviada e verificada: '{msg}'")
        else:
            print("Falha na verificação da mensagem")
            return False
    else:
        print("Objeto MessageSecurity não encontrado")
        return False
    
    print("\n5. Testando remoção de peer...")
    manager.remove_peer(peer_addr)
    if not manager.has_secure_connection(peer_addr):
        print(f"Peer {peer_addr} removido com sucesso")
        return True
    else:
        print("Falha ao remover peer")
        return False

def test_hmac_resistance():
    """Testa resistência do HMAC a ataques."""
    print_header("TESTE 4: RESISTÊNCIA DO HMAC")
    
    shared_key = b"chave_secreta_teste_1234567890!!"
    security = MessageSecurity(shared_key)
    
    msg = "Mensagem original"
    hmac_original = security.create_hmac(msg)
    
    print("\n1. Mensagem original:")
    print(f"Texto: '{msg}'")
    print(f"HMAC: {hmac_original}")
    
    print("\n2. Testando modificações mínimas...")
    
    # Teste 1: Adicionar um espaço
    msg_mod1 = msg + " "
    hmac_mod1 = security.create_hmac(msg_mod1)
    print(f"\na) Mensagem: '{msg_mod1}'")
    print(f"HMAC: {hmac_mod1}")
    if hmac_mod1 != hmac_original:
        print(f"Espaço detectado (HMACs diferentes)")
    else:
        print(f"Falha: HMACs iguais!")
        return False
    
    # Teste 2: Mudar uma letra
    msg_mod2 = msg.replace('i', 'I')
    hmac_mod2 = security.create_hmac(msg_mod2)
    print(f"\nb) Mensagem: '{msg_mod2}'")
    print(f"HMAC: {hmac_mod2}")
    if hmac_mod2 != hmac_original:
        print(f"Letra maiúscula detectada (HMACs diferentes)")
    else:
        print(f"Falha: HMACs iguais!")
        return False
    
    # Teste 3: Adicionar caractere
    msg_mod3 = msg + "!"
    hmac_mod3 = security.create_hmac(msg_mod3)
    print(f"\nc) Mensagem: '{msg_mod3}'")
    print(f"HMAC: {hmac_mod3}")
    if hmac_mod3 != hmac_original:
        print(f"Exclamação detectada (HMACs diferentes)")
        return True
    else:
        print(f"Falha: HMACs iguais!")
        return False

def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  TESTES DE SEGURANÇA - CHAT P2P SEGURO".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    results = []
    
    # Teste 1: Diffie-Hellman
    try:
        result1 = test_diffie_hellman()
        results.append(("Diffie-Hellman", result1))
    except Exception as e:
        print(f"\nERRO no teste Diffie-Hellman: {e}")
        results.append(("Diffie-Hellman", False))
    
    # Teste 2: HMAC
    try:
        result2 = test_hmac_integrity()
        results.append(("HMAC Integrity", result2))
    except Exception as e:
        print(f"\nERRO no teste HMAC: {e}")
        results.append(("HMAC Integrity", False))
    
    # Teste 3: Connection Manager
    try:
        result3 = test_secure_connection_manager()
        results.append(("Connection Manager", result3))
    except Exception as e:
        print(f"\nERRO no teste Connection Manager: {e}")
        results.append(("Connection Manager", False))
    
    # Teste 4: HMAC Resistance
    try:
        result4 = test_hmac_resistance()
        results.append(("HMAC Resistance", result4))
    except Exception as e:
        print(f"\nERRO no teste HMAC Resistance: {e}")
        results.append(("HMAC Resistance", False))
    
    # Resumo dos resultados
    print_header("RESUMO DOS TESTES")
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"  {test_name:.<50} {status}")
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed}/{total} testes passaram")
    print("-" * 70)
    
    if passed == total:
        print("\nTODOS OS TESTES PASSARAM! Sistema seguro e funcional.\n")
        return 0
    else:
        print(f"\n{total - passed} teste(s) falharam. Revisar implementação.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())