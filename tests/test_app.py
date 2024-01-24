from fastapi.testclient import TestClient
from gpt_engineer.api.app import app

client = TestClient(app)

def test_chat_with_knowledge():
    response = client.get("/chat", params={"input": "test"})
    assert response.status_code == 200
    assert response.json() == {"search_results": ["doc1", "doc2", "doc3"]}