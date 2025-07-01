# 🏙️ deuruimcidadao - Plataforma de Cidadania Ativa

## 📋 Descrição do Projeto

O **deuruimcidadao** é uma plataforma digital inovadora que conecta cidadãos e gestores públicos para resolver problemas urbanos de forma eficiente e transparente. O sistema permite que os cidadãos registrem reclamações sobre problemas da cidade (buracos, iluminação, limpeza, etc.) e acompanhem o progresso das soluções em tempo real.

### 🎯 Objetivo Principal

Criar uma ponte digital entre a população e os órgãos responsáveis, facilitando a comunicação, aumentando a transparência e promovendo a participação cidadã na melhoria das cidades.

## 🏗️ Arquitetura

Este projeto foi desenvolvido seguindo os princípios de **Clean Architecture** e **Clean Code**, garantindo:

- **Separação de responsabilidades** em camadas bem definidas
- **Baixo acoplamento** entre componentes
- **Alta coesão** dentro de cada módulo
- **Facilidade de testes** e manutenção
- **Escalabilidade** para crescimento futuro

### 📁 Estrutura do Projeto

```
deuruimcidadao/
├── app/                        # Aplicação principal
│   ├── domain/                 # Camada de Domínio (regras de negócio)
│   │   ├── entities/          # Entidades puras
│   │   │   ├── user.py        # Entidade User
│   │   │   ├── complaint.py   # Entidade Complaint
│   │   │   └── notification.py # Entidade Notification
│   │   └── models/            # Modelos de domínio
│   ├── usecases/              # Camada de Casos de Uso (lógica de aplicação)
│   │   ├── auth_usecases.py   # Casos de uso de autenticação
│   │   ├── complaint_usecases.py # Casos de uso de reclamações
│   │   ├── user_usecases.py   # Casos de uso de usuário
│   │   └── notification_usecases.py # Casos de uso de notificações
│   ├── infrastructure/        # Camada de Infraestrutura (frameworks, DB, APIs)
│   │   ├── db/               # Banco de dados
│   │   │   ├── database.py   # Configuração do banco
│   │   │   └── models.py     # Modelos SQLAlchemy
│   │   └── external/         # APIs externas
│   ├── interfaces/           # Camada de Interfaces (rotas, controllers)
│   │   ├── api/             # API REST
│   │   │   ├── auth_routes.py # Rotas de autenticação
│   │   │   ├── complaint_routes.py # Rotas de reclamações
│   │   │   ├── user_routes.py # Rotas de usuário
│   │   │   └── notification_routes.py # Rotas de notificações
│   │   └── web/             # Interface web
│   └── main.py              # Configuração principal da aplicação
├── src/                     # Arquivos estáticos (frontend)
│   └── static/             # HTML, CSS, JS
├── tests/                  # Testes
│   ├── unit/              # Testes unitários
│   └── integration/       # Testes de integração
├── uploads/               # Arquivos de upload
├── .env                   # Variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── requirements.txt      # Dependências Python
├── run.py               # Script de execução
└── README.md           # Este arquivo
```

## 🚀 Funcionalidades Implementadas

### 🔐 Sistema de Autenticação
- ✅ Registro de usuários com validação completa
- ✅ Login usando username, email ou CPF
- ✅ Autenticação JWT segura
- ✅ Logout
- ✅ Proteção de rotas
- ✅ Verificação de disponibilidade de username/email

### 👤 Perfil do Usuário
- ✅ Visualização do perfil
- ✅ Edição de dados pessoais
- ✅ Upload de foto de perfil
- ✅ Troca de senha
- ✅ Estatísticas do usuário

### 📝 Sistema de Reclamações
- ✅ Criação de reclamações com validação
- ✅ Listagem pública e pessoal
- ✅ Edição/exclusão de reclamações próprias
- ✅ Sistema de status (pendente, respondida, resolvida)
- ✅ Votação em reclamações
- ✅ Categorias predefinidas
- ✅ Filtros de busca

### 🔔 Sistema de Notificações
- ✅ Notificações in-app
- ✅ Marcação como lida
- ✅ Contagem de não lidas
- ✅ Filtros por tipo e canal

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Bcrypt**: Hash de senhas
- **SQLite**: Banco de dados
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização moderna
- **JavaScript ES6+**: Interatividade

### Arquitetura
- **Clean Architecture**: Separação em camadas
- **Clean Code**: Código limpo e legível
- **SOLID Principles**: Princípios de design
- **Dependency Injection**: Inversão de dependências

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd deuruimcidadao-teste
   ```

2. **Crie e ative o ambiente virtual**
   
   **Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env conforme necessário
   ```

5. **Execute a aplicação**
   ```bash
   python run.py
   ```
   
   Ou diretamente:
   ```bash
   python -m app.main
   ```

6. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 📡 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/check-username` - Verificar username
- `GET /api/auth/check-email` - Verificar email
- `GET /api/auth/me` - Dados do usuário atual

### Reclamações
- `GET /api/complaints` - Listar reclamações
- `POST /api/complaints` - Criar reclamação
- `GET /api/complaints/<id>` - Detalhes da reclamação
- `PUT /api/complaints/<id>` - Atualizar reclamação
- `DELETE /api/complaints/<id>` - Excluir reclamação
- `POST /api/complaints/<id>/vote` - Votar em reclamação
- `GET /api/complaints/my` - Minhas reclamações
- `GET /api/complaints/categories` - Categorias disponíveis

### Usuário
- `GET /api/users/profile` - Perfil do usuário
- `PUT /api/users/profile` - Atualizar perfil
- `PUT /api/users/change-password` - Alterar senha
- `POST /api/users/upload-avatar` - Upload de foto
- `GET /api/users/<id>` - Perfil público
- `GET /api/users/cities` - Cidades disponíveis

### Notificações
- `GET /api/notifications` - Listar notificações
- `PUT /api/notifications/<id>/read` - Marcar como lida
- `GET /api/notifications/unread-count` - Contagem não lidas
- `PUT /api/notifications/mark-all-read` - Marcar todas como lidas

## 🧪 Testes

Para executar os testes:

```bash
# Testes unitários
python -m pytest tests/unit/

# Testes de integração
python -m pytest tests/integration/

# Todos os testes
python -m pytest
```

## 🔧 Configuração

### Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Flask
SECRET_KEY=sua-chave-secreta
DEBUG=True

# Banco de Dados
DATABASE_URL=sqlite:///app.db

# JWT
JWT_SECRET_KEY=sua-chave-jwt
JWT_ACCESS_TOKEN_EXPIRES=3600

# Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

## 🤝 Contribuição

### Padrões de Código

- **Python**: PEP 8
- **Clean Code**: Funções pequenas, nomes significativos
- **Clean Architecture**: Separação de responsabilidades
- **SOLID**: Princípios de design orientado a objetos

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Desenvolvedor Principal**: [Seu Nome]
- **Arquitetura**: Clean Architecture & Clean Code

## 📞 Contato

- **Email**: contato@deuruimcidadao.com.br
- **GitHub**: https://github.com/DanAkiama/deuruimcidadao-teste

---

**deuruimcidadao** - Transformando cidades através da participação cidadã! 🏙️✨

### 🎯 Próximos Passos

- [ ] Implementar testes automatizados
- [ ] Adicionar sistema de cache
- [ ] Implementar notificações por email
- [ ] Adicionar geolocalização
- [ ] Criar painel administrativo
- [ ] Implementar sistema de gamificação

