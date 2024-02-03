import logging

from langchain.schema import AIMessage, HumanMessage, SystemMessage

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.dbs import DBs, archive
from gpt_engineer.core.chat_to_files import (
    format_file_to_input,
)


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
    
    def improve_existing_code(self, prompt: str):
        try:
            file_list = find_files_from_query(prompt)
            self.dbs.input.append(
                HISTORY_PROMPT_FILE, f"\n[[PROPMT]]\n{prompt}"
            )
            self.dbs.input.append(
                HISTORY_PROMPT_FILE, "\n[[PROPMT_FILES]]\n%s" % '\n'.join(file_list)
            )
            messages = [
                SystemMessage(content=self.setup_sys_prompt_existing_code(self.dbs)),
            ]

            for file_path in file_list:
                with open(file_path, 'r') as file:
                    file_content = format_file_to_input(file_path, file.readall())
                    messages.append(HumanMessage(content=f"{file_content}"))

            messages.append(HumanMessage(content=f"Request: {prompt}"))

            self.dbs.input.append(
                HISTORY_PROMPT_FILE, "\n[[AI_PROPMT]]\n%s" % "\n".join(
                    [str(msg) for msg in messages])
            )
            messages = self.ai.next(messages, step_name=curr_fn())

            response = messages[-1].content.strip()
            self.dbs.input.append(HISTORY_PROMPT_FILE, "\n[[AI]]\n%s" % response)

            self.overwrite_files_with_edits(chat)
        except Exception as ex:
            self.dbs.input.append(HISTORY_PROMPT_FILE, "\nERROR: %s" % str(ex))
            logging.error(f"[improve_existing_code] error: {ex}")

        return messages

    