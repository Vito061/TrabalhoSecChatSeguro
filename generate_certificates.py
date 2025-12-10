#!/usr/bin/env python3
"""
Script para gerar certificados SSL/TLS para o chat seguro.
Gera uma CA (Certificate Authority) e certificados para cada usuário.
"""

import os
import subprocess
from pathlib import Path

def criar_diretorio_certificados():
    """Cria a estrutura de diretórios para os certificados."""
    Path("TRACKER/certificates").mkdir(parents=True, exist_ok=True)
    os.chdir("TRACKER/certificates")

def gerar_ca():
    """Gera a Certificate Authority (CA)."""
    print("\n<SISTEMA>: Gerando Certificate Authority (CA)...")
    
    # Gera chave privada da CA
    subprocess.run([
        "openssl", "genrsa",
        "-out", "ca-key.pem",
        "4096"
    ], check=True)
    
    # Gera certificado da CA
    subprocess.run([
        "openssl", "req", "-new", "-x509",
        "-days", "365",
        "-key", "ca-key.pem",
        "-out", "ca-cert.pem",
        "-subj", "/C=BR/ST=DF/L=Brasilia/O=ChatP2P/CN=ChatP2P-CA"
    ], check=True)
    
    print("<SISTEMA>: CA gerada com sucesso!")

def gerar_certificado_usuario(username):
    """Gera certificado para um usuário específico."""
    print(f"\n<SISTEMA>: Gerando certificado para {username}...")
    
    # Gera chave privada do usuário
    subprocess.run([
        "openssl", "genrsa",
        "-out", f"{username}-key.pem",
        "4096"
    ], check=True)
    
    # Gera Certificate Signing Request (CSR)
    subprocess.run([
        "openssl", "req", "-new",
        "-key", f"{username}-key.pem",
        "-out", f"{username}-csr.pem",
        "-subj", f"/C=BR/ST=DF/L=Brasilia/O=ChatP2P/CN={username}"
    ], check=True)
    
    # Assina o certificado com a CA
    subprocess.run([
        "openssl", "x509", "-req",
        "-in", f"{username}-csr.pem",
        "-CA", "ca-cert.pem",
        "-CAkey", "ca-key.pem",
        "-CAcreateserial",
        "-out", f"{username}-cert.pem",
        "-days", "365"
    ], check=True)
    
    # Remove o CSR (não é mais necessário)
    os.remove(f"{username}-csr.pem")
    
    print(f"<SISTEMA>: Certificado para {username} gerado com sucesso!")

def main():
    """Função principal."""
    print("=" * 70)
    print("GERADOR DE CERTIFICADOS - CHAT P2P SEGURO")
    print("=" * 70)
    
    # Verifica se OpenSSL está instalado
    try:
        subprocess.run(["openssl", "version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("<SISTEMA>: ERRO - OpenSSL não encontrado!")
        print("<SISTEMA>: Instale o OpenSSL antes de continuar.")
        return
    
    criar_diretorio_certificados()
    
    # Gera CA se ainda não existe
    if not os.path.exists("ca-cert.pem"):
        gerar_ca()
    else:
        print("\n<SISTEMA>: CA já existe, pulando geração...")
    
    # Solicita nome do usuário
    username = input("\n<SISTEMA>: Digite o nome do usuário para gerar certificado: ")
    
    if os.path.exists(f"{username}-cert.pem"):
        print(f"<SISTEMA>: Certificado para {username} já existe!")
        resposta = input("<SISTEMA>: Deseja regenerar? (s/n): ")
        if resposta.lower() != 's':
            return
    
    gerar_certificado_usuario(username)
    
    print("\n" + "=" * 70)
    print("<SISTEMA>: Processo concluído!")
    print(f"<SISTEMA>: Arquivos gerados:")
    print(f"  - {username}-key.pem  (chave privada)")
    print(f"  - {username}-cert.pem (certificado)")
    print("=" * 70)

if __name__ == "__main__":
    main()