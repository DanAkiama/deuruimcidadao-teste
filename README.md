# 🏙️ deuruimcidadao - Plataforma de Cidadania Ativa

## 📋 Descrição do Projeto

O **deuruimcidadao** é uma plataforma digital inovadora que conecta cidadãos e gestores públicos para resolver problemas urbanos de forma eficiente e transparente. O sistema permite que os cidadãos registrem reclamações sobre problemas da cidade (buracos, iluminação, limpeza, etc.) e acompanhem o progresso das soluções em tempo real.

### 🎯 Objetivo Principal

Criar uma ponte digital entre a população e os órgãos responsáveis, facilitando a comunicação, aumentando a transparência e promovendo a participação cidadã na melhoria das cidades.

## 🚀 Funcionalidades Principais

### 👥 Sistema de Usuários
- **Cadastro Completo**: Nome, email, CPF, telefone, cidade
- **Dois Tipos de Usuário**:
  - **Cidadão**: Pode criar, votar e comentar reclamações
  - **Gestor Público**: Pode gerenciar e responder reclamações
- **Autenticação Segura**: Login com JWT, hash de senhas
- **Perfil Editável**: Foto, bio, configurações de privacidade

### 📝 Sistema de Reclamações
- **Categorias Inteligentes**: Buracos, iluminação, limpeza, trânsito, segurança
- **Upload de Mídia**: Fotos e vídeos para documentar problemas
- **Geolocalização**: Localização exata dos problemas
- **Sistema de Votação**: Evita duplicatas e prioriza problemas
- **Status Dinâmico**: Pendente → Em Andamento → Resolvida
- **Comentários**: Interação entre cidadãos e gestores

### 🎮 Gamificação
- **Sistema de Pontos**: XP por ações (criar reclamação, votar, etc.)
- **Níveis de Usuário**: Progressão baseada em atividade
- **Badges e Conquistas**: Reconhecimento por contribuições
- **Rankings**: Cidadãos mais ativos por cidade

### 🗺️ Integração com Mapas
- **Geocodificação**: Conversão endereço ↔ coordenadas
- **Mapa de Calor**: Visualização de densidade de problemas
- **Reclamações Próximas**: Busca por proximidade
- **Validação de Localização**: Verifica limites da cidade

### 🔔 Sistema de Notificações
- **Múltiplos Canais**: Email, WhatsApp, notificações push
- **Notificações Automáticas**: Status atualizado, novas respostas
- **Preferências Personalizáveis**: Controle total pelo usuário

### 📊 Painel Administrativo
- **Dashboard Completo**: Estatísticas em tempo real
- **Gerenciamento de Reclamações**: Filtros, busca, ações em lote
- **Relatórios**: Analytics e exportação de dados
- **Gestão de Usuários**: Visualizar, editar, suspender

### 🌐 Arquitetura Multi-cidade
- **Expansão Preparada**: Sistema pronto para múltiplas cidades
- **Seleção de Cidade**: No cadastro e navegação
- **Dados Isolados**: Cada cidade com seus próprios dados

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Bcrypt**: Hash de senhas
- **SQLite**: Banco de dados (desenvolvimento)
- **Geopy**: Funcionalidades geográficas

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização moderna com tema escuro
- **JavaScript ES6+**: Interatividade e AJAX
- **Responsive Design**: Compatível com mobile

### Funcionalidades Avançadas
- **Upload de Arquivos**: Pillow para processamento de imagens
- **Validação**: CPF, email, coordenadas geográficas
- **CORS**: Suporte para requisições cross-origin
- **Logging**: Sistema completo de logs

## 📁 Estrutura do Projeto

```
deuruimcidadao/
├── src/
│   ├── main.py                 # Arquivo principal da aplicação
│   ├── database.py             # Configuração do banco de dados
│   ├── models/                 # Modelos de dados
│   │   ├── __init__.py
│   │   ├── user.py            # Modelo de usuário
│   │   ├── complaint.py       # Modelo de reclamação
│   │   ├── notification.py    # Modelo de notificação
│   │   └── gamification.py    # Sistema de gamificação
│   ├── routes/                 # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py            # Autenticação
│   │   ├── complaints.py      # Reclamações
│   │   ├── user_profile.py    # Perfil do usuário
│   │   ├── admin.py           # Painel administrativo
│   │   ├── notifications.py   # Notificações
│   │   └── maps.py            # Mapas e geolocalização
│   ├── services/               # Serviços auxiliares
│   │   ├── notification_service.py
│   │   └── maps_service.py
│   ├── static/                 # Arquivos estáticos
│   │   ├── index.html         # Página principal
│   │   ├── dashboard.html     # Dashboard do usuário
│   │   ├── profile.html       # Página de perfil
│   │   ├── admin.html         # Painel administrativo
│   │   ├── styles.css         # Estilos CSS
│   │   ├── script.js          # JavaScript principal
│   │   ├── dashboard.js       # JS do dashboard
│   │   ├── profile.js         # JS do perfil
│   │   └── admin.js           # JS do admin
│   └── database/               # Banco de dados
│       └── app.db             # SQLite database
├── venv/                       # Ambiente virtual Python
├── requirements.txt            # Dependências Python
└── README.md                   # Este arquivo
```

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone ou extraia o projeto**
   ```bash
   # Se você recebeu um arquivo ZIP, extraia-o
   # Se está clonando: git clone <url-do-repositorio>
   cd deuruimcidadao
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

4. **Execute a aplicação**
   ```bash
   python src/main.py
   ```

5. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

### 🔧 Configuração Adicional

#### Variáveis de Ambiente (Opcional)
Crie um arquivo `.env` na raiz do projeto para configurações personalizadas:

```env
# Configurações do Flask
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui

# Configurações de Email (para notificações)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# Configurações do WhatsApp (API externa)
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_TOKEN=seu-token-aqui

# Configurações de Mapas
MAPS_API_KEY=sua-chave-do-google-maps
```

## 📱 Como Usar a Plataforma

### Para Cidadãos

1. **Cadastro**
   - Acesse a página inicial
   - Clique em "Cadastrar"
   - Preencha seus dados (nome, email, CPF, cidade)
   - Selecione "Cidadão" como tipo de usuário

2. **Fazer uma Reclamação**
   - Faça login na plataforma
   - Acesse o Dashboard
   - Clique em "Nova Reclamação"
   - Preencha: título, descrição, categoria, localização
   - Adicione fotos se necessário
   - Envie a reclamação

3. **Acompanhar Reclamações**
   - Visualize suas reclamações no perfil
   - Receba notificações sobre atualizações
   - Vote em reclamações de outros cidadãos
   - Comente e interaja

### Para Gestores Públicos

1. **Cadastro**
   - Cadastre-se selecionando "Gestor Público"
   - Aguarde aprovação (se necessário)

2. **Gerenciar Reclamações**
   - Acesse o painel administrativo
   - Visualize todas as reclamações da cidade
   - Filtre por status, categoria, prioridade
   - Atualize status das reclamações
   - Responda aos cidadãos

3. **Relatórios e Analytics**
   - Visualize estatísticas da cidade
   - Exporte relatórios
   - Analise tendências e padrões

## 🎨 Design e Interface

### Tema Escuro
- **Cores principais**: Tons de azul, roxo e cinza
- **Contraste otimizado**: Reduz fadiga visual
- **Acessibilidade**: Compatível com leitores de tela

### Responsividade
- **Mobile First**: Otimizado para dispositivos móveis
- **Breakpoints**: Tablet e desktop
- **Touch Friendly**: Botões e elementos adequados para toque

### Micro-interações
- **Animações suaves**: Transições de 300ms
- **Feedback visual**: Estados hover, focus, active
- **Loading states**: Indicadores de carregamento

## 🔒 Segurança

### Autenticação
- **JWT Tokens**: Sessões seguras e stateless
- **Hash de Senhas**: Bcrypt com salt
- **Validação de Dados**: Sanitização de inputs

### Privacidade
- **LGPD Compliant**: Exportação e exclusão de dados
- **Configurações de Privacidade**: Controle pelo usuário
- **Dados Mínimos**: Coleta apenas o necessário

## 📊 APIs Disponíveis

### Autenticação
- `POST /api/auth/register` - Cadastro de usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/check-username` - Verificar disponibilidade
- `GET /api/auth/check-email` - Verificar email

### Reclamações
- `GET /api/complaints` - Listar reclamações
- `POST /api/complaints` - Criar reclamação
- `GET /api/complaints/<id>` - Detalhes da reclamação
- `PUT /api/complaints/<id>` - Atualizar reclamação
- `DELETE /api/complaints/<id>` - Excluir reclamação
- `POST /api/complaints/<id>/vote` - Votar em reclamação

### Perfil
- `GET /api/profile` - Dados do perfil
- `PUT /api/profile` - Atualizar perfil
- `POST /api/profile/upload-avatar` - Upload de foto
- `PUT /api/profile/change-password` - Alterar senha

### Notificações
- `GET /api/notifications` - Listar notificações
- `PUT /api/notifications/<id>/read` - Marcar como lida
- `GET /api/notifications/unread-count` - Contagem não lidas

### Mapas
- `POST /api/maps/geocode` - Converter endereço em coordenadas
- `GET /api/maps/nearby-complaints` - Reclamações próximas
- `GET /api/maps/heatmap` - Dados para mapa de calor

### Admin (Gestores)
- `GET /api/admin/dashboard` - Estatísticas do painel
- `GET /api/admin/complaints` - Gerenciar reclamações
- `PUT /api/admin/complaints/<id>/status` - Atualizar status
- `GET /api/admin/users` - Gerenciar usuários

## 🚀 Próximos Passos e Melhorias

### Funcionalidades Futuras
- [ ] **App Mobile**: React Native ou Flutter
- [ ] **Integração com Prefeituras**: APIs oficiais
- [ ] **Chatbot**: Atendimento automatizado
- [ ] **Reconhecimento de Imagem**: Categorização automática
- [ ] **Blockchain**: Transparência e imutabilidade
- [ ] **IA para Priorização**: Machine Learning para urgência

### Melhorias Técnicas
- [ ] **Banco de Dados**: Migração para PostgreSQL
- [ ] **Cache**: Redis para performance
- [ ] **CDN**: Distribuição de conteúdo
- [ ] **Monitoramento**: Logs e métricas avançadas
- [ ] **Testes**: Cobertura completa de testes
- [ ] **CI/CD**: Pipeline de deploy automatizado

### Expansão
- [ ] **Mais Cidades**: Cuiabá, Várzea Grande, Campo Grande
- [ ] **Estados**: Mato Grosso, Mato Grosso do Sul
- [ ] **Nacional**: Expansão para todo o Brasil
- [ ] **Internacional**: Adaptação para outros países

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código
- **Python**: PEP 8
- **JavaScript**: ES6+ com Prettier
- **CSS**: BEM methodology
- **Commits**: Conventional Commits

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Desenvolvedor Principal**: [Seu Nome]
- **Design**: [Nome do Designer]
- **Product Owner**: [Nome do PO]

## 📞 Contato

- **Email**: contato@deuruimcidadao.com.br
- **Website**: https://deuruimcidadao.com.br
- **GitHub**: https://github.com/deuruimcidadao
- **LinkedIn**: https://linkedin.com/company/deuruimcidadao

## 🙏 Agradecimentos

- Comunidade Flask por um framework incrível
- Contribuidores open source
- Cidadãos que acreditam na mudança através da tecnologia
- Gestores públicos comprometidos com a transparência

---

**deuruimcidadao** - Transformando cidades através da participação cidadã! 🏙️✨

