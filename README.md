# To Do List API

API simples de To Do List usando FastAPI e MongoDB Atlas.

## Configuração

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
```

## Executando a aplicação

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Endpoints e Exemplos

### 1. Criar uma nova lista
```bash
curl -X POST http://localhost:8000/lists/ \
-H "Content-Type: application/json" \
-H "Accept: application/json"
```

Resposta:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [],
    "created_at": "2024-03-14T12:00:00.000Z"
}
```

### 2. Obter uma lista específica
```bash
curl -X GET http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000 \
-H "Accept: application/json"
```

Resposta:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
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

### 3. Adicionar um item à lista
```bash
curl -X POST http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/ \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
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

### 4. Marcar/desmarcar um item como concluído
```bash
curl -X PUT http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/item-uuid-1 \
-H "Accept: application/json"
```

Resposta:
```json
{
    "message": "Item atualizado com sucesso"
}
```

### 5. Remover um item da lista
```bash
curl -X DELETE http://localhost:8000/lists/550e8400-e29b-41d4-a716-446655440000/items/item-uuid-1 \
-H "Accept: application/json"
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