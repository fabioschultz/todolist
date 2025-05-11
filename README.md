# To Do List API

API simples de To Do List usando FastAPI e MongoDB Atlas.

## Configuração

### Opção 1: Execução Local

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo .env:
- Crie um arquivo `.env` na raiz do projeto
- Adicione as seguintes variáveis:
```
MONGODB_URL=sua_url_do_mongodb_atlas
DATABASE_NAME=todo_db
API_KEY=sua_api_key_secreta
```

4. Execute a aplicação:
```bash
uvicorn main:app --reload
```

### Opção 2: Execução com Docker

1. Certifique-se de ter o Docker e o Docker Compose instalados

2. Construa e inicie os containers:
```bash
docker-compose up --build
```

3. Para parar os containers:
```bash
docker-compose down
```

A API estará disponível em `http://localhost:8000`

## Autenticação

A API requer uma API Key para autenticação. A API Key deve ser enviada no header `X-API-Key` em todas as requisições.

Exemplo:
```bash
curl -H "X-API-Key: sua_api_key_secreta" http://localhost:8000/lists/
```

## Endpoints e Exemplos

### 1. Criar uma nova lista
```bash
curl -X POST http://localhost:8000/lists/ \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta" \
-d '{
    "name": "Lista de Compras",
    "user_id": "user123"
}'
```

Resposta:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Lista de Compras",
    "user_id": "user123",
    "items": [],
    "created_at": "2024-03-14T12:00:00.000Z"
}
```

### 2. Obter uma lista específica
```bash
curl -X GET http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000 \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta"
```

Resposta:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Lista de Compras",
    "user_id": "user123",
    "items": [
        {
            "id": "item-uuid-1",
            "text": "Minha primeira tarefa",
            "done": false,
            "created_at": "2024-03-14T12:00:00.000Z"
        }
    ],
    "created_at": "2024-03-14T12:00:00.000Z"
}
```

### 3. Obter todas as listas de um usuário
```bash
curl -X GET http://localhost:8000/lists/user/user123 \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta"
```

Resposta:
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Lista de Compras",
        "user_id": "user123",
        "items": [...],
        "created_at": "2024-03-14T12:00:00.000Z"
    },
    {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "name": "Tarefas do Trabalho",
        "user_id": "user123",
        "items": [...],
        "created_at": "2024-03-14T12:00:00.000Z"
    }
]
```

### 4. Adicionar um item à lista
```bash
curl -X POST http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/ \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta" \
-d '{
    "text": "Minha primeira tarefa"
}'
```

Resposta:
```json
{
    "id": "item-uuid-1",
    "text": "Minha primeira tarefa",
    "done": false,
    "created_at": "2024-03-14T12:00:00.000Z"
}
```

### 5. Marcar/desmarcar um item como concluído
```bash
curl -X PUT http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/item-uuid-1 \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta"
```

Resposta:
```json
{
    "message": "Item atualizado com sucesso"
}
```

### 6. Remover um item da lista
```bash
curl -X DELETE http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/item-uuid-1 \
-H "Accept: application/json" \
-H "X-API-Key: sua_api_key_secreta"
```

Resposta:
```json
{
    "message": "Item removido com sucesso"
}
```

## Documentação

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 