# Guia Rápido - Chat P2P Seguro

## ⚡ Instalação Rápida (5 minutos)

### Passo 1: Verificar Requisitos
```bash
# Python 3.8+
python3 --version

# OpenSSL
openssl version
```

### Passo 2: Estrutura de Diretórios
```bash
# Criar estrutura necessária
mkdir -p TRACKER/certificates
mkdir -p TRACKER/userinfo
mkdir -p TRACKER/logs
touch TRACKER/__init__.py
touch TRACKER/userinfo/__init__.py
touch TRACKER/logs/__init__.py
```

### Passo 3: Criar logger.py
```bash
# Criar TRACKER/logs/logger.py
cat > TRACKER/logs/logger.py << 'EOF'
from datetime import datetime

class Logger:
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("TRACKER/logs/chat.log", "a") as f:
            f.write(f"[{timestamp}] {msg}\n")

logger = Logger()
EOF
```

### Passo 4: Gerar Certificados
```bash
# Para Alice
python3 generate_certificates.py
# Digite: alice

# Para Bob (em outro terminal/máquina)
python3 generate_certificates.py
# Digite: bob
```

**Importante:** Se estiver testando em máquinas diferentes, copie o arquivo `ca-cert.pem` para ambas!

### Passo 5: Executar

**Terminal 1 (Alice):**
```bash
python3 main.py
# Usuário: alice
# Senha: senha123 (defina uma)
# Confirme: senha123
# Porta: 5000
```

**Terminal 2 (Bob):**
```bash
python3 main.py
# Usuário: bob
# Senha: senha456 (defina uma)
# Confirme: senha456
# Porta: 5001
```

### Passo 6: Conectar
No terminal de Alice:
```bash
/connect <IP_DO_BOB>:5001
```

Exemplo local:
```bash
/connect 127.0.0.1:5001
```

### Passo 7: Enviar Mensagens
Simplesmente digite e pressione Enter:
```bash
Olá Bob! Canal seguro estabelecido!
```

---

## 🔍 Verificação Rápida

### Ver Status de Segurança
```bash
/secure_status
```

Deve mostrar:
```
<SISTEMA>: Conexões seguras estabelecidas:
  • 127.0.0.1:5001
```

### Testar Componentes
```bash
python3 test_security.py
```

Deve mostrar:
```
  Diffie-Hellman................................ ✅ PASSOU
  HMAC Integrity................................. ✅ PASSOU
  Connection Manager............................. ✅ PASSOU
  HMAC Resistance................................ ✅ PASSOU

🎉 TODOS OS TESTES PASSARAM!
```

---

## 🐛 Troubleshooting Rápido

### Erro: "Certificados não encontrados"
```bash
# Solução:
python3 generate_certificates.py
```

### Erro: "OpenSSL não encontrado"
```bash
# Ubuntu/Debian:
sudo apt install openssl

# Windows:
# Baixar de: https://slproweb.com/products/Win32OpenSSL.html
```

### Erro: "Conexão recusada"
```bash
# Verificar se o outro peer está rodando:
# No terminal de Bob, deve aparecer:
# <SISTEMA>: Servidor SEGURO inicializado (mTLS ativo)

# Verificar IP correto:
ip addr  # Linux
ipconfig # Windows
```

### Erro: "ERRO SSL - Autenticação falhou"
```bash
# Causas comuns:
# 1. Certificado não gerado
python3 generate_certificates.py

# 2. CA diferente entre peers
# Solução: Copiar o MESMO ca-cert.pem para ambas as máquinas

# 3. Nome no certificado diferente do usuário
# Solução: Regenerar certificado com nome correto
```

---

## 📊 Comandos Essenciais

| Comando | Descrição |
|---------|-----------|
| `/connect IP:PORTA` | Conecta a um peer |
| `/peers` | Lista peers conhecidos |
| `/secure_status` | Status das conexões seguras |
| `/disconnect IP:PORTA` | Desconecta de um peer |
| `/menu` | Lista todos os comandos |
| `/clear` | Limpa a tela |

---

## 🎯 Cenários de Teste

### Teste 1: Conexão Segura Básica
1. Iniciar Alice (porta 5000)
2. Iniciar Bob (porta 5001)
3. Alice: `/connect 127.0.0.1:5001`
4. Verificar: "Conexão SEGURA estabelecida"
5. Enviar mensagens

✅ **Sucesso:** Mensagens trafegam com HMAC

### Teste 2: Verificar Wireshark
1. Abrir Wireshark: `sudo wireshark`
2. Capturar interface (eth0, wlan0, etc.)
3. Filtro: `tcp.port == 5000 or tcp.port == 5001`
4. Estabelecer conexão
5. Enviar mensagens
6. Verificar: Dados aparecem como "Encrypted Application Data"

✅ **Sucesso:** Pacotes criptografados (não legíveis)

### Teste 3: Integridade
1. Conectar Alice e Bob
2. Enviar mensagem normal
3. Modificar código para adulterar HMAC (ver README)
4. Enviar mensagem adulterada
5. Verificar: Alerta "INTEGRIDADE VIOLADA"

✅ **Sucesso:** Adulteração detectada

---

## 📁 Arquivos Necessários

```
projeto/
├── main.py                    ✅ Obrigatório
├── client.py                  ✅ Obrigatório
├── server.py                  ✅ Obrigatório
├── security.py                ✅ Obrigatório
├── utils.py                   ✅ Obrigatório
├── peersdb.py                 ✅ Obrigatório
├── generate_certificates.py   ✅ Obrigatório
├── test_security.py           ⭐ Recomendado
├── TRACKER/
│   ├── __init__.py           ✅ Obrigatório
│   ├── certificates/          ✅ Obrigatório (vazio inicialmente)
│   ├── userinfo/
│   │   ├── __init__.py       ✅ Obrigatório
│   │   └── userinfo.py       ✅ Obrigatório
│   ├── logs/
│   │   ├── __init__.py       ✅ Obrigatório
│   │   └── logger.py         ✅ Obrigatório
│   └── salasdb.py            ⭐ Opcional (para salas)
└── README.md                  📖 Documentação
```

---

## ⏱️ Timeline de Uso

**Primeira Execução (10 min):**
1. Instalar requisitos (2 min)
2. Criar estrutura (1 min)
3. Gerar certificados (2 min)
4. Executar e testar (5 min)

**Execuções Seguintes (1 min):**
1. `python3 main.py`
2. Login
3. Conectar

---

## 💡 Dicas Rápidas

### Teste Local (Uma Máquina)
```bash
# Terminal 1:
python3 main.py  # alice, porta 5000

# Terminal 2:
python3 main.py  # bob, porta 5001

# Terminal 1 (Alice):
/connect 127.0.0.1:5001
```

### Teste em Rede (Duas Máquinas)
```bash
# Máquina 1 (Alice):
ip addr  # Anotar IP: 192.168.1.100
python3 main.py  # porta 5000

# Máquina 2 (Bob):
python3 main.py  # porta 5001
/connect 192.168.1.100:5000
```

### Copiar CA para Outra Máquina
```bash
# Na máquina que gerou primeiro:
scp TRACKER/certificates/ca-cert.pem user@192.168.1.101:/path/to/project/TRACKER/certificates/
```

---

## ✅ Checklist de Funcionamento

Antes de apresentar, verifique:

- [ ] OpenSSL instalado
- [ ] Python 3.8+ instalado
- [ ] Certificados gerados para todos os usuários
- [ ] `ca-cert.pem` compartilhado entre máquinas (se aplicável)
- [ ] Estrutura de diretórios criada
- [ ] Logger criado (`TRACKER/logs/logger.py`)
- [ ] Teste básico: conexão estabelecida
- [ ] Teste de segurança: `python3 test_security.py` passa
- [ ] Wireshark instalado (para demonstração)
- [ ] Firewall permite portas (5000, 5001, etc.)

---

## 🆘 Suporte Rápido

### Comando não funciona?
```bash
/menu  # Ver todos os comandos
```

### Esqueceu a senha?
```bash
/resignin  # Recadastrar usuário
```

### Perda de conexão?
```bash
/disconnect IP:PORTA  # Desconectar
/connect IP:PORTA     # Reconectar
```

### Logs de debug?
```bash
# Ver logs:
cat TRACKER/logs/chat.log

# Limpar logs:
rm TRACKER/logs/chat.log
```

---

## 🚀 Pronto para Usar!

Se todos os passos foram seguidos, você deve ver:

```
======================================================================
CHAT P2P SEGURO - FUNCIONALIDADES IMPLEMENTADAS
======================================================================

🔒 SEGURANÇA DA INFORMAÇÃO:
  ✓ mTLS (mutual TLS) - Autenticação mútua cliente/servidor
  ✓ Certificados Digitais X.509 - Identidade verificada
  ✓ Diffie-Hellman - Troca segura de chaves de sessão
  ✓ HMAC-SHA256 - Garantia de integridade das mensagens
  ✓ SSL/TLS - Confidencialidade do canal de comunicação
```

**Agora é só usar! 🎉**

Digite sua primeira mensagem e veja a mágica da criptografia em ação! 🔐