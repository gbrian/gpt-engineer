import typer

from gpt_engineer.core.db import DB

from gpt_engineer.knowledge.knowledge_prompts import KnowledgePrompts
from gpt_engineer.knowledge.knowledge import Knowledge

app = typer.Typer()

db = DB("preprompts")
knowledge_prompts = KnowledgePrompts(db)

@app.command()
def knowledge(
    path: str, 
    index: bool = typer.Option(False, "--index", "-i", help="Reload documents.")
  ):
    kr = Knowledge(path=path, knowledge_prompts=knowledge_prompts)
    if index:
        kr.reload()
    
    query = input("Search?")
    if query:
      documents = kr.search(query)
      print(f"Documents for {query}")
      print(documents)

if __name__ == "__main__":
    app()