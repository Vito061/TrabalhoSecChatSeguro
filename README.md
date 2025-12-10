# Chat P2P Seguro (WhatsChat)

## Descrição

Aplicação de chat peer-to-peer seguro que implementa os três pilares da segurança da informação:

- **Confidencialidade**: Comunicação criptografada via TLS/SSL
- **Autenticidade**: Autenticação mútua com certificados digitais (mTLS)
- **Integridade**: Verificação de mensagens com HMAC-SHA256

## Funcionalidades de Segurança Implementadas

### 1. mTLS (Mutual TLS)
- Autenticação mútua entre cliente e servidor
- Cada usuário possui seu próprio certificado digital X.509
- Certificados assinados por uma CA (Certificate Authority) local
- Impede conexões de usuários não autorizados

### 2. Diffie-Hellman
- Troca segura de chaves de sessão
- Estabelece segredo compartilhado sem transmitir a chave pela rede
- Usa grupo MODP de 2048 bits (RFC 3526)
- Chave derivada com SHA-256

### 3. HMAC-SHA256
- Garante integridade de cada mensagem
- Detecta qualquer adulteração durante o tráfego
- Alertas automáticos quando integridade é violada
- Usa a chave estabelecida via Diffie-Hellman

## Instalação e Configuração

### Pré-requisitos

```bash
# Python 3.8 ou superior
python3 --version

# OpenSSL (para geração de certificados)
openssl version
```

### Instalação no Linux (Ubuntu/Debian)

```bash
# Instalar OpenSSL (se necessário)
sudo apt update
sudo apt install openssl python3

# Clonar/baixar o projeto
cd /caminho/do/projeto
```

### Instalação no Windows

```bash
# Baixar OpenSSL de: https://slproweb.com/products/Win32OpenSSL.html
# Instalar Python de: https://www.python.org/downloads/
```

## Passo a Passo de Uso

### 1. Gerar Certificados

**Primeiro usuário:**
```bash
python generate_certificates.py
# Digite: alice
```

**Segundo usuário (em outra máquina/terminal):**
```bash
python generate_certificates.py
# Digite: bob
```

Isso criará:
- `TRACKER/certificates/ca-cert.pem` (Certificate Authority)
- `TRACKER/certificates/alice-cert.pem` e `alice-key.pem`
- `TRACKER/certificates/bob-cert.pem` e `bob-key.pem`

### 2. Executar a Aplicação

**Terminal 1 (Alice):**
```bash
python main.py
# Login: alice
# Senha: (defina uma senha)
# Porta: 5000
```

**Terminal 2 (Bob):**
```bash
python main.py
# Login: bob
# Senha: (defina uma senha)
# Porta: 5001
```

### 3. Conectar os Peers

No terminal de Alice:
```bash
/connect 192.168.1.100:5001
```

Você verá:
```
======================================================================
<SISTEMA>: Conexão SEGURA estabelecida com 192.168.1.100:5001
<SISTEMA>: Certificado do peer verificado: bob
<SISTEMA>: Troca de chaves DH concluída com bob
<SISTEMA>: Chave de sessão estabelecida com 192.168.1.100:5001
<SISTEMA>: Canal seguro pronto para troca de mensagens
======================================================================
```

### 4. Verificar Status de Segurança

```bash
/secure_status
```

Saída:
```
<SISTEMA>: Conexões seguras estabelecidas:
  • 192.168.1.100:5001
```

### 5. Enviar Mensagens Seguras

Simplesmente digite sua mensagem:
```bash
Olá Bob! Esta mensagem está protegida com HMAC!
```

## Demonstração Experimental

### Verificar Confidencialidade (Wireshark)

1. Abra o Wireshark
2. Capture tráfego na interface de rede
3. Filtre por porta: `tcp.port == 5000`
4. Observe que os dados estão criptografados (TLS)
5. Compare com chat sem TLS (texto plano visível)

**Resultado esperado:**
```
Application Data (criptografado)
TLS 1.2/1.3 Record Layer
```

### Verificar Autenticidade

1. Tente conectar sem certificado válido
2. A conexão será rejeitada
3. Mensagem: "ERRO SSL - Autenticação falhou"

### Verificar Integridade

Para testar, você pode modificar o código temporariamente para enviar uma mensagem adulterada:

```python
# Em client.py, modifique temporariamente:
package = security.package_message(msg)
# Adulterar: package = package.replace("a", "b")
c.sendall(package.encode('utf-8'))
```

**Resultado esperado:**
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
<SISTEMA>: ⚠️  ALERTA DE SEGURANÇA  ⚠️
<SISTEMA>: Mensagem com INTEGRIDADE VIOLADA!
<SISTEMA>: Origem: 192.168.1.100:5001
<SISTEMA>: A mensagem pode ter sido ADULTERADA!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## Comandos Disponíveis

### Conexão
- `/connect <IP:PORTA>` - Conecta a um peer com mTLS
- `/disconnect <IP:PORTA>` - Desconecta de um peer
- `/peers` - Lista peers conhecidos
- `/connections` - Lista conexões ativas

### Segurança
- `/secure_status` - Status das conexões seguras
- `/security_info` - Informações detalhadas de segurança

### Salas
- `/create_room <nome> <porta> <senha>` - Cria sala privada
- `/enter_room <nome> [senha]` - Entra em uma sala

### Sistema
- `/clear` - Limpa a tela
- `/menu` - Exibe menu de comandos
- `/resignin` - Recadastrar usuário

## Testes para o Relatório

### Teste 1: Confidencialidade
1. Iniciar Wireshark
2. Conectar dois peers
3. Enviar mensagens
4. Capturar pacotes e mostrar que estão criptografados
5. **Screenshot**: Pacotes TLS no Wireshark

### Teste 2: Autenticidade
1. Tentar conectar sem certificado
2. Mostrar erro de autenticação
3. Conectar com certificado válido
4. Mostrar verificação bem-sucedida
5. **Screenshot**: Logs de autenticação

### Teste 3: Integridade
1. Enviar mensagem normal (aceita)
2. Enviar mensagem adulterada (rejeitada)
3. Mostrar alerta de integridade violada
4. **Screenshot**: Alerta de segurança

## Estrutura de Arquivos

```
projeto/
├── main.py                          # Aplicação principal
├── client.py                        # Cliente seguro (mTLS)
├── server.py                        # Servidor seguro (mTLS)
├── security.py                      # DH + HMAC
├── generate_certificates.py         # Gerador de certificados
├── utils.py                         # Funções auxiliares
├── peersdb.py                       # Banco de dados de peers
├── TRACKER/
│   ├── certificates/                # Certificados SSL/TLS
│   │   ├── ca-cert.pem
│   │   ├── ca-key.pem
│   │   ├── alice-cert.pem
│   │   ├── alice-key.pem
│   │   ├── bob-cert.pem
│   │   └── bob-key.pem
│   ├── userinfo/
│   │   ├── userinfo.py              # Gerenciamento de usuários
│   │   └── user.json                # Credenciais
│   ├── logs/
│   │   └── logger.py                # Sistema de logs
│   └── salasdb.py                   # Gerenciamento de salas
└── README.md                        # Este arquivo
```

## Fluxo de Segurança

1. **Conexão Inicial**
   - Cliente solicita conexão TCP
   - Servidor aceita e inicia handshake TLS
   - Troca de certificados (mTLS)
   - Validação mútua dos certificados pela CA

2. **Estabelecimento de Chave de Sessão**
   - Cliente gera par de chaves Diffie-Hellman
   - Cliente envia chave pública ao servidor
   - Servidor gera seu par DH e envia chave pública
   - Ambos calculam segredo compartilhado
   - Chave derivada com SHA-256

3. **Comunicação Segura**
   - Mensagem é empacotada com HMAC
   - Formato: `{"msg": "texto", "hmac": "hash"}`
   - Transmissão via canal TLS
   - Receptor verifica HMAC antes de exibir

## Observações Importantes

1. **Certificados**: Gere certificados para cada usuário antes de usar
2. **CA**: A Certificate Authority é compartilhada entre todos os usuários
3. **Portas**: Use portas diferentes para cada instância (5000, 5001, etc.)
4. **Firewall**: Certifique-se de que as portas estejam abertas
5. **Rede**: Para testes locais, use `localhost` ou IPs da rede local

## Bibliotecas Utilizadas

- **ssl**: TLS/SSL para confidencialidade e mTLS
- **hashlib**: SHA-256 para derivação de chaves e hashing
- **hmac**: HMAC-SHA256 para integridade
- **secrets**: Geração de números aleatórios criptograficamente seguros
- **socket**: Comunicação TCP/IP
- **threading**: Suporte a múltiplas conexões simultâneas
- **json**: Serialização de dados

## Conceitos Demonstrados

1. **mTLS (Mutual TLS Authentication)**
   - Autenticação bidirecional
   - Verificação de certificados
   - PKI (Public Key Infrastructure)

2. **Diffie-Hellman Key Exchange**
   - Troca de chaves sem canal seguro prévio
   - Segredo compartilhado calculado localmente
   - Resistente a ataques de interceptação

3. **HMAC (Hash-based Message Authentication Code)**
   - Verificação de integridade
   - Autenticação de origem
   - Detecção de adulterações

4. **Confidencialidade via TLS**
   - Criptografia de dados em trânsito
   - Proteção contra escuta (eavesdropping)
   - Verificável com análise de pacotes

## Troubleshooting

### Erro: "Certificados não encontrados"
**Solução**: Execute `python generate_certificates.py`

### Erro: "OpenSSL não encontrado"
**Solução Linux**: `sudo apt install openssl`
**Solução Windows**: Baixe de https://slproweb.com/products/Win32OpenSSL.html

### Erro: "ERRO SSL - Autenticação falhou"
**Causas possíveis**:
- Certificado expirado (regenere com generate_certificates.py)
- CA diferente entre os peers (compartilhe o ca-cert.pem)
- Certificado não assinado pela CA correta

### Erro: "Conexão recusada"
**Soluções**:
- Verifique se o servidor está rodando
- Confirme o IP e porta corretos
- Verifique firewall/antivírus

## Suporte

Para dúvidas sobre implementação ou conceitos de segurança, consulte:
- RFC 5246 (TLS 1.2)
- RFC 2104 (HMAC)
- RFC 3526 (Diffie-Hellman Groups)
- Documentação Python ssl: https://docs.python.org/3/library/ssl.html

## Checklist de Requisitos Atendidos

- [x] Login de usuário (com senha criptografada)
- [x] Listagem de usuários participantes (/peers)
- [x] Canal de comunicação seguro (mTLS)
- [x] Autenticação mútua (certificados digitais)
- [x] Confidencialidade (TLS/SSL)
- [x] Integridade (HMAC-SHA256)
- [x] Verificação de integridade com alertas
- [x] Verificação de autenticidade (validação de certificados)
- [x] Demonstração experimental (Wireshark)
- [x] Troca segura de chaves (Diffie-Hellman)

---

**Desenvolvido para demonstrar os pilares da Segurança da Informação: Confidencialidade, Autenticidade e Integridade.**
