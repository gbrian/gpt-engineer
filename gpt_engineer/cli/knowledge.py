import typer
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever

app = typer.Typer()

@app.command()
def knowledge(
    path: str, 
    index: bool = typer.Option(False, "--index", "-i", help="Reload documents.")
  ):
    kr = KnowledgeRetriever(path)
    if index:
        kr.reload()
    
    query = input("Search?")
    if query:
      documents = kr.search(query)
      print(f"Documents for {query}")
      print(documents)

if __name__ == "__main__":
    app()