from fastapi import FastAPI, HTTPException
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

app = FastAPI(title="To Do List API")

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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    done: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TodoList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[TodoItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

@app.post("/lists/", response_model=TodoList)
async def create_list():
    todo_list = TodoList()
    await todos_collection.insert_one(todo_list.dict())
    return todo_list

@app.get("/lists/{list_id}", response_model=TodoList)
async def get_list(list_id: str):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return todo_list

@app.post("/lists/{list_id}/items/", response_model=TodoItem)
async def add_item(list_id: str, item: TodoItem):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    await todos_collection.update_one(
        {"id": list_id},
        {"$push": {"items": item.dict()}}
    )
    return item

@app.put("/lists/{list_id}/items/{item_id}")
async def toggle_item(list_id: str, item_id: str):
    todo_list = await todos_collection.find_one({"id": list_id})
    if not todo_list:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    item = next((item for item in todo_list["items"] if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    item["done"] = not item["done"]
    await todos_collection.update_one(
        {"id": list_id, "items.id": item_id},
        {"$set": {"items.$.done": item["done"]}}
    )
    return {"message": "Item atualizado com sucesso"}

@app.delete("/lists/{list_id}/items/{item_id}")
async def delete_item(list_id: str, item_id: str):
    result = await todos_collection.update_one(
        {"id": list_id},
        {"$pull": {"items": {"id": item_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return {"message": "Item removido com sucesso"} 