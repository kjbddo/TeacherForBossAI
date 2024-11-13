# qa_service.py

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks.manager import get_openai_callback

class QAService:
    """질의응답(QA) 서비스 관리 클래스."""

    def __init__(self, db_directory: str, model_name="gpt-3.5-turbo-0125", temperature=0.1, max_tokens=1100):
        self.db_directory = db_directory
        self.embedding = OpenAIEmbeddings()
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=0.5,
            frequency_penalty=0.5
        )
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "이 시스템은 자영업 관련 질문에 답변할 수 있습니다. user의 문제를 분석하여 적절한 해결방안 혹은 방향성을 제시할 수 있습니다. user입장에서 가장 이득이 될 수 있도록 자영업과 관련된 사회의 시스템을 소개해야 합니다. 답변은 항상 전문가와의 상담을 권고합니다."),
            ("user", "{user_input}")
        ])
        self.output_parser = StrOutputParser()

    def qacall(self, query: str) -> str:
        vectordb = Chroma(persist_directory=self.db_directory, embedding_function=self.embedding).as_retriever()
        qa_chain = self.chat_prompt | self.llm | self.output_parser

        with get_openai_callback() as cb:
            response = qa_chain.invoke(query)

        return {"response": response}
