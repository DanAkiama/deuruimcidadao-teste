# 🚀 Guia de Instalação - deuruimcidadao

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em seu sistema:

- **Python 3.8 ou superior** ([Download aqui](https://python.org/downloads/))
- **pip** (gerenciador de pacotes Python - geralmente vem com Python)
- **Git** (opcional, para clonar repositórios)

### Verificando Instalações

```bash
# Verificar versão do Python
python --version
# ou
python3 --version

# Verificar pip
pip --version
# ou
pip3 --version
```

## 💻 Instalação por Sistema Operacional

### 🐧 Linux (Ubuntu/Debian)

1. **Atualizar sistema**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Instalar Python e pip (se necessário)**
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. **Navegar para o diretório do projeto**
   ```bash
   cd /caminho/para/deuruimcidadao
   ```

4. **Criar ambiente virtual**
   ```bash
   python3 -m venv venv
   ```

5. **Ativar ambiente virtual**
   ```bash
   source venv/bin/activate
   ```

6. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

7. **Executar aplicação**
   ```bash
   python src/main.py
   ```

### 🍎 macOS

1. **Instalar Homebrew (se não tiver)**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Instalar Python**
   ```bash
   brew install python
   ```

3. **Navegar para o diretório do projeto**
   ```bash
   cd /caminho/para/deuruimcidadao
   ```

4. **Criar ambiente virtual**
   ```bash
   python3 -m venv venv
   ```

5. **Ativar ambiente virtual**
   ```bash
   source venv/bin/activate
   ```

6. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

7. **Executar aplicação**
   ```bash
   python src/main.py
   ```

### 🪟 Windows

1. **Baixar e instalar Python**
   - Acesse [python.org](https://python.org/downloads/)
   - Baixe a versão mais recente
   - **IMPORTANTE**: Marque "Add Python to PATH" durante a instalação

2. **Abrir PowerShell ou Prompt de Comando**
   - Pressione `Win + R`, digite `powershell` e pressione Enter

3. **Navegar para o diretório do projeto**
   ```powershell
   cd C:\caminho\para\deuruimcidadao
   ```

4. **Criar ambiente virtual**
   ```powershell
   python -m venv venv
   ```

5. **Ativar ambiente virtual**
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Ou no Prompt de Comando
   venv\Scripts\activate.bat
   ```

6. **Instalar dependências**
   ```powershell
   pip install -r requirements.txt
   ```

7. **Executar aplicação**
   ```powershell
   python src/main.py
   ```

## 🐳 Instalação com Docker (Opcional)

Se você preferir usar Docker:

1. **Criar Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["python", "src/main.py"]
   ```

2. **Construir imagem**
   ```bash
   docker build -t deuruimcidadao .
   ```

3. **Executar container**
   ```bash
   docker run -p 5000:5000 deuruimcidadao
   ```

## 🔧 Configuração Inicial

### 1. Configurar Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações básicas
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-super-segura-aqui

# Configurações de banco de dados
DATABASE_URL=sqlite:///src/database/app.db

# Configurações de email (para notificações)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# Configurações do WhatsApp (opcional)
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_TOKEN=seu-token-aqui

# Configurações de mapas (opcional)
MAPS_API_KEY=sua-chave-do-google-maps
```

### 2. Configurar Email para Notificações (Opcional)

Para ativar notificações por email:

1. **Gmail**: 
   - Ative a verificação em 2 etapas
   - Gere uma senha de app
   - Use a senha de app no arquivo `.env`

2. **Outros provedores**:
   - Configure SMTP_SERVER e SMTP_PORT adequadamente

### 3. Primeiro Acesso

1. **Acesse a aplicação**
   ```
   http://localhost:5000
   ```

2. **Crie sua conta**
   - Clique em "Cadastrar"
   - Preencha seus dados
   - Selecione sua cidade
   - Escolha o tipo de usuário

3. **Explore as funcionalidades**
   - Dashboard
   - Criar reclamações
   - Perfil do usuário
   - (Se for gestor) Painel administrativo

## 🚨 Solução de Problemas

### Erro: "python não é reconhecido"
**Windows**: Python não foi adicionado ao PATH
- Reinstale o Python marcando "Add Python to PATH"
- Ou adicione manualmente: `C:\Python3X\` e `C:\Python3X\Scripts\`

### Erro: "pip não encontrado"
```bash
# Linux/macOS
sudo apt install python3-pip  # Ubuntu/Debian
brew install python           # macOS

# Windows
python -m ensurepip --upgrade
```

### Erro: "Permissão negada" (Linux/macOS)
```bash
# Use sudo apenas se necessário
sudo pip install -r requirements.txt

# Ou prefira usar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Porta 5000 já está em uso"
```bash
# Encontrar processo usando a porta
lsof -i :5000  # Linux/macOS
netstat -ano | findstr :5000  # Windows

# Matar processo
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Ou usar outra porta
export FLASK_RUN_PORT=5001  # Linux/macOS
set FLASK_RUN_PORT=5001     # Windows
```

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de que o ambiente virtual está ativo
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstale as dependências
pip install -r requirements.txt
```

### Banco de dados não criado
```bash
# Execute o Python no diretório do projeto
cd deuruimcidadao
python -c "from src.main import app; app.app_context().push(); from src.database import db; db.create_all()"
```

## 🔄 Atualizações

Para atualizar o projeto:

1. **Baixe a nova versão**
2. **Ative o ambiente virtual**
3. **Atualize dependências**
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. **Execute migrações (se houver)**
5. **Reinicie a aplicação**

## 📱 Acesso Mobile

A aplicação é responsiva e funciona em dispositivos móveis:

- **Navegador mobile**: Acesse `http://seu-ip:5000`
- **Rede local**: Outros dispositivos na mesma rede podem acessar usando seu IP

Para encontrar seu IP:
```bash
# Linux/macOS
ifconfig | grep inet

# Windows
ipconfig
```

## 🌐 Deploy em Produção

Para deploy em servidor:

1. **Use um servidor WSGI**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

2. **Configure proxy reverso** (Nginx)
3. **Use HTTPS** (Let's Encrypt)
4. **Configure banco de dados** (PostgreSQL)
5. **Configure backup automático**

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** da aplicação
2. **Consulte a documentação** completa no README.md
3. **Abra uma issue** no repositório
4. **Entre em contato**: contato@deuruimcidadao.com.br

---

**Boa sorte com sua instalação! 🚀**

