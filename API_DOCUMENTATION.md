# 📡 Documentação da API - deuruimcidadao

## 🔗 Base URL
```
http://localhost:5000/api
```

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Após o login, inclua o token no header das requisições:

```http
Authorization: Bearer <seu-jwt-token>
```

## 📋 Endpoints Disponíveis

### 🔑 Autenticação

#### POST /auth/register
Cadastra um novo usuário no sistema.

**Request Body:**
```json
{
  "full_name": "Maria Santos Silva",
  "username": "maria_santos",
  "email": "maria@email.com",
  "cpf": "12345678901",
  "phone": "65999887766",
  "city": "cuiaba",
  "role": "cidadao",
  "password": "senha123"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Usuário cadastrado com sucesso",
  "user": {
    "id": 1,
    "username": "maria_santos",
    "email": "maria@email.com",
    "full_name": "Maria Santos Silva",
    "city": "cuiaba",
    "role": "cidadao"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/login
Realiza login no sistema.

**Request Body:**
```json
{
  "login": "maria_santos",  // username, email ou CPF
  "password": "senha123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "user": {
    "id": 1,
    "username": "maria_santos",
    "email": "maria@email.com",
    "full_name": "Maria Santos Silva",
    "city": "cuiaba",
    "role": "cidadao"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/logout
Realiza logout (invalida o token).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Logout realizado com sucesso"
}
```

#### GET /auth/check-username
Verifica se um username está disponível.

**Query Parameters:**
- `username`: Nome de usuário a verificar

**Response (200):**
```json
{
  "available": true,
  "message": "Username disponível"
}
```

#### GET /auth/check-email
Verifica se um email está disponível.

**Query Parameters:**
- `email`: Email a verificar

**Response (200):**
```json
{
  "available": true,
  "message": "Email disponível"
}
```

### 📝 Reclamações

#### GET /complaints
Lista reclamações com filtros e paginação.

**Query Parameters:**
- `page`: Página (padrão: 1)
- `per_page`: Itens por página (padrão: 10, máx: 50)
- `status`: Filtro por status (pendente, em_andamento, resolvida, respondida)
- `category`: Filtro por categoria (buracos, iluminacao, limpeza, transito, seguranca, outros)
- `priority`: Filtro por prioridade (baixa, media, alta, urgente)
- `city`: Filtro por cidade
- `search`: Busca por título ou descrição
- `sort`: Ordenação (created_at, votes, priority)
- `order`: Ordem (asc, desc)

**Response (200):**
```json
{
  "success": true,
  "complaints": [
    {
      "id": 1,
      "title": "Buraco na Rua das Flores",
      "description": "Grande buraco causando transtornos...",
      "category": "buracos",
      "status": "pendente",
      "priority": "alta",
      "location": "Rua das Flores, 123",
      "latitude": -15.6014,
      "longitude": -56.0979,
      "city": "cuiaba",
      "created_at": "2024-06-28T10:30:00Z",
      "updated_at": "2024-06-28T10:30:00Z",
      "user": {
        "id": 1,
        "username": "maria_santos",
        "full_name": "Maria Santos Silva"
      },
      "votes_count": 24,
      "user_voted": false,
      "images": [
        "/uploads/complaints/1/image1.jpg"
      ],
      "responses_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 156,
    "pages": 16,
    "has_next": true,
    "has_prev": false
  }
}
```

#### POST /complaints
Cria uma nova reclamação.

**Headers:** `Authorization: Bearer <token>`

**Request Body (multipart/form-data):**
```json
{
  "title": "Buraco na Rua das Flores",
  "description": "Grande buraco causando transtornos no trânsito",
  "category": "buracos",
  "priority": "alta",
  "location": "Rua das Flores, 123",
  "latitude": -15.6014,
  "longitude": -56.0979,
  "images": [<arquivo1>, <arquivo2>]  // Opcional
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Reclamação criada com sucesso",
  "complaint": {
    "id": 1,
    "title": "Buraco na Rua das Flores",
    "description": "Grande buraco causando transtornos no trânsito",
    "category": "buracos",
    "status": "pendente",
    "priority": "alta",
    "location": "Rua das Flores, 123",
    "latitude": -15.6014,
    "longitude": -56.0979,
    "city": "cuiaba",
    "created_at": "2024-06-28T10:30:00Z",
    "protocol": "CBA-2024-001"
  }
}
```

#### GET /complaints/{id}
Obtém detalhes de uma reclamação específica.

**Response (200):**
```json
{
  "success": true,
  "complaint": {
    "id": 1,
    "title": "Buraco na Rua das Flores",
    "description": "Grande buraco causando transtornos no trânsito",
    "category": "buracos",
    "status": "pendente",
    "priority": "alta",
    "location": "Rua das Flores, 123",
    "latitude": -15.6014,
    "longitude": -56.0979,
    "city": "cuiaba",
    "created_at": "2024-06-28T10:30:00Z",
    "updated_at": "2024-06-28T10:30:00Z",
    "protocol": "CBA-2024-001",
    "user": {
      "id": 1,
      "username": "maria_santos",
      "full_name": "Maria Santos Silva",
      "avatar": "/uploads/profiles/1/avatar.jpg"
    },
    "votes_count": 24,
    "user_voted": false,
    "images": [
      "/uploads/complaints/1/image1.jpg",
      "/uploads/complaints/1/image2.jpg"
    ],
    "responses": [
      {
        "id": 1,
        "message": "Reclamação recebida e encaminhada para a equipe responsável",
        "created_at": "2024-06-28T11:00:00Z",
        "user": {
          "full_name": "João Gestor",
          "role": "gestor_publico"
        }
      }
    ]
  }
}
```

#### PUT /complaints/{id}
Atualiza uma reclamação (apenas o autor).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Novo título",
  "description": "Nova descrição",
  "category": "iluminacao",
  "priority": "media"
}
```

#### DELETE /complaints/{id}
Exclui uma reclamação (apenas o autor).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Reclamação excluída com sucesso"
}
```

#### POST /complaints/{id}/vote
Vota em uma reclamação.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Voto registrado com sucesso",
  "votes_count": 25,
  "user_voted": true
}
```

#### DELETE /complaints/{id}/vote
Remove voto de uma reclamação.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Voto removido com sucesso",
  "votes_count": 24,
  "user_voted": false
}
```

#### POST /complaints/{id}/response
Adiciona resposta a uma reclamação (gestores).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "message": "Equipe técnica foi acionada para resolver o problema"
}
```

### 👤 Perfil do Usuário

#### GET /profile
Obtém dados do perfil do usuário logado.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "maria_santos",
    "email": "maria@email.com",
    "full_name": "Maria Santos Silva",
    "cpf": "12345678901",
    "phone": "65999887766",
    "city": "cuiaba",
    "role": "cidadao",
    "bio": "Cidadã ativa preocupada com a cidade",
    "avatar": "/uploads/profiles/1/avatar.jpg",
    "created_at": "2024-06-01T10:00:00Z",
    "last_activity": "2024-06-28T15:30:00Z",
    "stats": {
      "complaints_count": 12,
      "resolved_count": 8,
      "votes_received": 156,
      "votes_given": 89,
      "points": 1250,
      "level": 5
    },
    "badges": [
      {
        "name": "Cidadão Ativo",
        "description": "10 reclamações registradas",
        "icon": "star",
        "earned_at": "2024-06-15T10:00:00Z"
      }
    ]
  }
}
```

#### PUT /profile
Atualiza dados do perfil.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "Maria Santos Silva",
  "phone": "65999887766",
  "bio": "Nova biografia"
}
```

#### POST /profile/upload-avatar
Faz upload da foto de perfil.

**Headers:** `Authorization: Bearer <token>`

**Request Body (multipart/form-data):**
```
avatar: <arquivo-imagem>
```

#### PUT /profile/change-password
Altera a senha do usuário.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha",
  "confirm_password": "nova_senha"
}
```

### 🔔 Notificações

#### GET /notifications
Lista notificações do usuário.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Página (padrão: 1)
- `per_page`: Itens por página (padrão: 20)
- `unread_only`: Apenas não lidas (true/false)

**Response (200):**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "complaint_status_updated",
      "title": "Status da reclamação atualizado",
      "message": "Sua reclamação 'Buraco na Rua das Flores' foi atualizada para 'Em Andamento'",
      "read": false,
      "created_at": "2024-06-28T14:30:00Z",
      "data": {
        "complaint_id": 1,
        "old_status": "pendente",
        "new_status": "em_andamento"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 5,
    "pages": 1
  }
}
```

#### PUT /notifications/{id}/read
Marca notificação como lida.

**Headers:** `Authorization: Bearer <token>`

#### PUT /notifications/mark-all-read
Marca todas as notificações como lidas.

**Headers:** `Authorization: Bearer <token>`

#### GET /notifications/unread-count
Obtém contagem de notificações não lidas.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "unread_count": 3
}
```

### 🗺️ Mapas e Geolocalização

#### POST /maps/geocode
Converte endereço em coordenadas.

**Request Body:**
```json
{
  "address": "Rua das Flores, 123",
  "city": "cuiaba"
}
```

**Response (200):**
```json
{
  "success": true,
  "location": {
    "address": "Rua das Flores, 123, Cuiabá - MT",
    "latitude": -15.6014,
    "longitude": -56.0979,
    "city": "cuiaba",
    "neighborhood": "Centro"
  }
}
```

#### POST /maps/reverse-geocode
Converte coordenadas em endereço.

**Request Body:**
```json
{
  "latitude": -15.6014,
  "longitude": -56.0979
}
```

#### GET /maps/nearby-complaints
Busca reclamações próximas a uma localização.

**Query Parameters:**
- `latitude`: Latitude
- `longitude`: Longitude
- `radius`: Raio em km (padrão: 1.0)
- `limit`: Limite de resultados (padrão: 10)

#### GET /maps/heatmap
Obtém dados para mapa de calor.

**Query Parameters:**
- `city`: Cidade
- `status`: Filtro por status

### 🛡️ Admin (Gestores Públicos)

#### GET /admin/dashboard
Obtém estatísticas do painel administrativo.

**Headers:** `Authorization: Bearer <token>` (gestor)

**Response (200):**
```json
{
  "success": true,
  "stats": {
    "complaints": {
      "total": 1247,
      "pending": 156,
      "in_progress": 42,
      "resolved": 892,
      "urgent": 23
    },
    "users": {
      "total": 3247,
      "citizens": 3198,
      "managers": 49,
      "active_today": 234
    },
    "satisfaction": {
      "average": 4.3,
      "total_ratings": 567
    },
    "trends": {
      "complaints_this_month": 89,
      "resolved_this_month": 67,
      "response_time_avg": 2.5
    }
  }
}
```

#### GET /admin/complaints
Lista reclamações para gestão (com filtros avançados).

**Headers:** `Authorization: Bearer <token>` (gestor)

#### PUT /admin/complaints/{id}/status
Atualiza status de uma reclamação.

**Headers:** `Authorization: Bearer <token>` (gestor)

**Request Body:**
```json
{
  "status": "em_andamento",
  "message": "Equipe técnica foi acionada"
}
```

#### GET /admin/users
Lista usuários para gestão.

**Headers:** `Authorization: Bearer <token>` (gestor)

## 📊 Códigos de Status HTTP

- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Erro de validação
- **401**: Não autorizado
- **403**: Acesso negado
- **404**: Não encontrado
- **409**: Conflito (ex: email já existe)
- **422**: Dados inválidos
- **500**: Erro interno do servidor

## 🔒 Segurança

### Rate Limiting
- **Geral**: 100 requisições por minuto por IP
- **Login**: 5 tentativas por minuto por IP
- **Upload**: 10 uploads por minuto por usuário

### Validações
- **CPF**: Validação de formato e dígitos verificadores
- **Email**: Validação de formato RFC 5322
- **Coordenadas**: Validação de limites geográficos
- **Imagens**: Tipos permitidos (JPEG, PNG, WebP), tamanho máximo 5MB

### Headers de Segurança
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## 📝 Exemplos de Uso

### Fluxo Completo: Criar Reclamação

1. **Registrar usuário**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Maria Santos",
    "username": "maria_santos",
    "email": "maria@email.com",
    "cpf": "12345678901",
    "city": "cuiaba",
    "role": "cidadao",
    "password": "senha123"
  }'
```

2. **Fazer login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "maria_santos",
    "password": "senha123"
  }'
```

3. **Criar reclamação**
```bash
curl -X POST http://localhost:5000/api/complaints \
  -H "Authorization: Bearer <token>" \
  -F "title=Buraco na rua" \
  -F "description=Grande buraco causando problemas" \
  -F "category=buracos" \
  -F "priority=alta" \
  -F "location=Rua das Flores, 123" \
  -F "latitude=-15.6014" \
  -F "longitude=-56.0979" \
  -F "images=@foto1.jpg"
```

### JavaScript/Fetch

```javascript
// Login
const login = async () => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      login: 'maria_santos',
      password: 'senha123'
    })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
};

// Listar reclamações
const getComplaints = async () => {
  const response = await fetch('/api/complaints?page=1&per_page=10', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  return await response.json();
};
```

## 🐛 Tratamento de Erros

### Formato de Erro Padrão
```json
{
  "success": false,
  "message": "Descrição do erro",
  "errors": {
    "field_name": ["Erro específico do campo"]
  },
  "code": "ERROR_CODE"
}
```

### Códigos de Erro Comuns
- `VALIDATION_ERROR`: Erro de validação
- `AUTHENTICATION_REQUIRED`: Token necessário
- `INVALID_CREDENTIALS`: Credenciais inválidas
- `PERMISSION_DENIED`: Sem permissão
- `RESOURCE_NOT_FOUND`: Recurso não encontrado
- `DUPLICATE_ENTRY`: Entrada duplicada

---

**Para mais informações, consulte o código fonte ou entre em contato com a equipe de desenvolvimento.**

