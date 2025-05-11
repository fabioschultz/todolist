from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    return api_key_header

app = FastAPI(
    title="To Do List API",
    description="""
    API para gerenciamento de listas de tarefas (To Do List).
    
    ## Funcionalidades
    
    * Criar novas listas de tarefas
    * Adicionar itens às listas
    * Marcar itens como concluídos
    * Remover itens
    * Consultar listas específicas
    * Consultar todas as listas de um usuário
    
    ## Autenticação
    
    Esta API requer uma API Key para autenticação.
    A API Key deve ser enviada no header `X-API-Key`.
    
    ## Estrutura de Dados
    
    Cada lista possui um UUID único, um nome, um ID de usuário e contém uma coleção de itens.
    Cada item possui seu próprio UUID, texto, status de conclusão e data de criação.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração do MongoDB com SSL
client = AsyncIOMotorClient(
    os.getenv("MONGODB_URL"),
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    maxPoolSize=50,
    minPoolSize=10
)
db = client[os.getenv("DATABASE_NAME")]
todos_collection = db.todos

class TodoItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID único do item")
    text: str = Field(..., description="Texto da tarefa")
    done: bool = Field(default=False, description="Status de conclusão da tarefa")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data e hora de criação")

    class Config:
        schema_extra = {
            "example": {
                "text": "Comprar leite",
                "done": False
            }
        }

class TodoList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID único da lista")
    name: str = Field(..., description="Nome da lista")
    user_id: str = Field(..., description="ID do usuário dono da lista")
    items: List[TodoItem] = Field(default_factory=list, description="Lista de itens")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data e hora de criação")

    class Config:
        schema_extra = {
            "example": {
                "name": "Lista de Compras",
                "user_id": "user123"
            }
        }

@app.post("/lists/", 
    response_model=TodoList,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova lista",
    description="Cria uma nova lista de tarefas vazia e retorna seu UUID.",
    dependencies=[Depends(get_api_key)]
)
async def create_list(list_data: TodoList):
    await todos_collection.insert_one(list_data.dict())
    return list_data

@app.get("/lists/{list_id}", 
    response_model=TodoList,
    summary="Obter lista",
    description="Retorna uma lista específica pelo seu UUID.",
    responses={
        404: {"description": "Lista não encontrada"}
    },
    dependencies=[Depends(get_api_key)]
)
async def get_list(list_id: str):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista não encontrada"
        )
    return todo_list

@app.get("/lists/user/{user_id}", 
    response_model=List[TodoList],
    summary="Obter listas do usuário",
    description="Retorna todas as listas de um usuário específico.",
    responses={
        404: {"description": "Nenhuma lista encontrada para este usuário"}
    },
    dependencies=[Depends(get_api_key)]
)
async def get_user_lists(user_id: str):
    cursor = todos_collection.find({"user_id": user_id})
    lists = await cursor.to_list(length=None)
    if not lists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma lista encontrada para este usuário"
        )
    return lists

@app.post("/lists/{list_id}/items/", 
    response_model=TodoItem,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar item",
    description="Adiciona um novo item à lista especificada.",
    responses={
        404: {"description": "Lista não encontrada"}
    },
    dependencies=[Depends(get_api_key)]
)
async def add_item(list_id: str, item: TodoItem):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista não encontrada"
        )
    
    await todos_collection.update_one(
        {"id": list_id},
        {"$push": {"items": item.dict()}}
    )
    return item

@app.put("/lists/{list_id}/items/{item_id}",
    summary="Atualizar item",
    description="Marca ou desmarca um item como concluído.",
    responses={
        404: {"description": "Lista ou item não encontrado"}
    },
    dependencies=[Depends(get_api_key)]
)
async def toggle_item(list_id: str, item_id: str):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista não encontrada"
        )
    
    item = next((item for item in todo_list["items"] if item["id"] == item_id), None)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    
    item["done"] = not item["done"]
    await todos_collection.update_one(
        {"id": list_id, "items.id": item_id},
        {"$set": {"items.$.done": item["done"]}}
    )
    return {"message": "Item atualizado com sucesso"}

@app.delete("/lists/{list_id}/items/{item_id}",
    summary="Remover item",
    description="Remove um item específico da lista.",
    responses={
        404: {"description": "Item não encontrado"}
    },
    dependencies=[Depends(get_api_key)]
)
async def delete_item(list_id: str, item_id: str):
    result = await todos_collection.update_one(
        {"id": list_id},
        {"$pull": {"items": {"id": item_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    return {"message": "Item removido com sucesso"} 