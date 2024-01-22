from fastapi import FastAPI

api = FastAPI()

@api.get("/chat")
def chat_with_knowledge(input: str):
    # Perform search on Knowledge using the input
    # Return the search results as response
    
    # Placeholder code for now
    search_results = ["doc1", "doc2", "doc3"]
    return {"search_results": search_results}
