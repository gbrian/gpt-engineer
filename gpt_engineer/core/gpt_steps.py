import logging

from langchain.schema import AIMessage, HumanMessage, SystemMessage

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.dbs import DBs, archive


class GPTSteps:
    ai: AI = None
    dbs: DBs = None

    def __init__(self, ai: AI, dbs: DBs):
        self.ai = ai
        self.dbs = dbs


    def setup_sys_prompt_existing_code(self) -> str:
        return (
            self.dbs.preprompts["improve"].replace(
                "FILE_FORMAT", self.dbs.preprompts["file_format"])
            + "\nUseful to know:\n"
            + self.dbs.preprompts["philosophy"]
        )


    def find_files_from_query(self, query: str) -> [str]:
        file_list = []
        documents = self.dbs.knowledge.search(query)
        self.dbs.input.append(
            HISTORY_PROMPT_FILE, f"\n[[KNOWLEDGE]]\n{documents}"
        )
        if documents:
            # Filter out irrelevant documents based on a relevance score
            relevant_documents = [doc for doc in parallel_validate_contexts(
                dbs, query, documents) if doc]
            file_list = [str(Path(doc.metadata["source"]).absolute())
                        for doc in relevant_documents]
            file_list = list(dict.fromkeys(file_list))  # Remove duplicates
        return file_list
    
    def improve_existing_code(self):
        file_list = find_files_from_query(prompt)

        messages = [
            SystemMessage(content=self.setup_sys_prompt_existing_code(self.dbs)),
        ]

        for code_input in file_list:
            if code_input:
                messages.append(HumanMessage(content=f"{code_input}"))

        messages.append(HumanMessage(content=f"Request: {self.dbs.input[PROMPT_FILE]}"))

        self.dbs.input.append(
            HISTORY_PROMPT_FILE, "\n[[AI_PROPMT]]\n%s" % "\n".join(
                [str(msg) for msg in messages])
        )
        messages = ai.next(messages, step_name=curr_fn())

        chat = messages[-1].content.strip()
        self.dbs.input.append(HISTORY_PROMPT_FILE, "\n[[AI]]\n%s" % chat)
        try:
            self.overwrite_files_with_edits(chat)
        except Exception as ex:
            self.dbs.input.append(HISTORY_PROMPT_FILE, "\nERROR: %s" % str(ex))
            logging.error(f"[improve_existing_code] error: {ex}")

        return messages

    