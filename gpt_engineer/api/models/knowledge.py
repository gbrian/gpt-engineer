from pydantic import BaseModel

class KnowledgeReloadPath(BaseModel):
    path: str


class KnowledgeSearch(BaseModel):
    search_term: str
    search_type: str