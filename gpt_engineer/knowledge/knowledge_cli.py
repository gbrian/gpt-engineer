import argparse
import logging

from gpt_engineer.settings import KNOWLEDGE_PATH
from gpt_engineer.knowledge.knowledge_search import KnowledgeSearch
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever
from langchain.text_splitter import Language

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Knowledge CLI')
    parser.add_argument('-p', '--prompt', type=str, help='Ask a question to the Knowledge')
    parser.add_argument('--create-index', action='store_true', help='Create a new knowledge index')

    args = parser.parse_args()

    if args.create_index:
        logger.info('Creating a new knowledge index...')
        try:
            loader = KnowledgeRetriever.from_documents(KNOWLEDGE_PATH, ['.py'], 'python')
            logger.info('Knowledge index created successfully.')
        except Exception as e:
            logger.error(f'Error while creating knowledge index: {e}')

    if args.prompt:
        logger.info(f'Asking question: {args.prompt}')
        try:
            chat = KnowledgeSearch(KNOWLEDGE_PATH, suffixes=['.py'], language=Language.PYTHON)
            answer = chat.ask_question(args.prompt)
            print(answer)
            logger.info('Question answered successfully.')
        except Exception as e:
            logger.error(f'Error while asking question: {e}')

if __name__ == "__main__":
    main()