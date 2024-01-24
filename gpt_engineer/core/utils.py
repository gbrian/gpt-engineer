import inspect
from pathlib import Path

def curr_fn() -> str:
    return inspect.stack()[1].function

def document_to_context(doc):
    return "\n".join([
      f"```{doc.metadata.get('language')}",
      f"{Path(doc.metadata['source']).absolute()}",
      doc.page_content,
      "```"
    ])
