from fastapi import FastAPI
from gpt_engineer.api.model import ChatMessage, Message 
from gpt_engineer.api.app_service import clarify_business_request


class GPTEngineerAPI:
    def __init__(self, dbs:DBS):
        self.dbs = dbs

    def start(self):
        app = FastAPI()

        @app.get("/health")
        def health_check():
            return "ok"

        @app.post("/chat")
        def chat(chat_message: ChatMessage):
            # Perform search on Knowledge using the input
            # Return the search results as response
            
            # Placeholder code for now
            search_results = ["doc1", "doc2", "doc3"]
            return {"message": message, "search_results": search_results}

        return app