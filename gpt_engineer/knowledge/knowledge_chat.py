class KnowledgeChat:
    def __init__(self, llm, retriever, memory):
        self.llm = llm
        self.retriever = retriever
        self.memory = memory

    @classmethod
    def from_llm(cls, llm, retriever, memory):
        return cls(llm, retriever, memory)

    def ask_question(self, question):
        # Ask a question and get an answer
        pass