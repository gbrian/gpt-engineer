from fastapi import FastAPI
from pydantic import BaseModel

class Message(BaseModel):
    user: str
    message: str

app = FastAPI()

@app.get("/health")
def chat_with_knowledge():
  return "ok"

@app.post("/chat")
def chat_with_knowledge(message: Message):
    # Perform search on Knowledge using the input
    # Return the search results as response
    
    # Placeholder code for now
    search_results = ["doc1", "doc2", "doc3"]
    return {"message": message, "search_results": search_results}
