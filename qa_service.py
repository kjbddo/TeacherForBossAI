from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks.manager import get_openai_callback


def create_prompt(category: str, content: str, extra_data: dict, relevant_text: str = "") -> str:
    """카테고리 및 추가 데이터에 따라 동적으로 프롬프트를 생성"""

    # 기본적인 프롬프트 구조 설정
    prompt_template = "자영업 관련하여 다음과 같은 구체적은 해결책을 제공합니다. 마지막에는 항상 전문가와의 상담을 권고합니다.\n\n"

    # 관련 텍스트가 있으면 추가
    if relevant_text:
        prompt_template += f"참고 정보:\n{relevant_text}\n\n"

    # 카테고리별 프롬프트 구성
    if category == "노하우" or category == "상권":
        prompt_template += "상세한 자영업 노하우를 바탕으로 한 매장 운영 조언을 드립니다.\n"
        if extra_data:
            if extra_data.get("bossType"):
                prompt_template += f"- 창업자 유형: {extra_data['bossType']}\n"
            if extra_data.get("businessType"):
                prompt_template += f"- 업종 및 주요 메뉴: {extra_data['businessType']}\n"
            if extra_data.get("location"):
                prompt_template += f"- 매장 위치 및 규모: {extra_data['location']}\n"
            if extra_data.get("customerType"):
                prompt_template += f"- 주요 고객 및 목표 고객: {extra_data['customerType']}\n"
            if extra_data.get("storeInfo"):
                prompt_template += f"- 매장 정보: {extra_data['storeInfo']}\n"
            if extra_data.get("budget"):
                prompt_template += f"- 가용 예산: {extra_data['budget']}\n"

    elif category == "세무":
        prompt_template += "자영업자를 위한 세무 조언을 제공합니다.\n"
        if extra_data:
            if extra_data.get("taxBookKeepingStatus"):
                prompt_template += f"- 세무 기장 상태: {extra_data['taxBookKeepingStatus']}\n"
            if extra_data.get("businessType"):
                prompt_template += f"- 업종 및 개업연월일: {extra_data['businessType']}\n"
            if extra_data.get("branchInfo"):
                prompt_template += f"- 사업장 정보: {extra_data['branchInfo']}\n"
            if extra_data.get("employeeManagement"):
                prompt_template += f"- 직원 관리 정보: {extra_data['employeeManagement']}\n"
            if extra_data.get("purchaseEvidence"):
                prompt_template += f"- 구입 증빙 방법: {extra_data['purchaseEvidence']}\n"
            if extra_data.get("salesScale"):
                prompt_template += f"- 매출 규모: {extra_data['salesScale']}\n"

    elif category == "직원관리":
        prompt_template += "자영업 매장의 직원 관리와 관련된 조언을 제공합니다.\n"
        if extra_data:
            if extra_data.get("contractStatus"):
                prompt_template += f"- 근로계약서 상태: {extra_data['contractStatus']}\n"
            if extra_data.get("businessType"):
                prompt_template += f"- 업종 및 개업연월일: {extra_data['businessType']}\n"
            if extra_data.get("employmentTypeAndDuration"):
                prompt_template += f"- 직원 고용 형태 및 기간: {extra_data['employmentTypeAndDuration']}\n"
            if extra_data.get("workAndBreakHours"):
                prompt_template += f"- 근로 및 휴게 시간: {extra_data['workAndBreakHours']}\n"
            if extra_data.get("salaryAndAllowance"):
                prompt_template += f"- 급여 및 수당 체계: {extra_data['salaryAndAllowance']}\n"
            if extra_data.get("statutoryBenefits"):
                prompt_template += f"- 법정 복리후생 제공 여부: {extra_data['statutoryBenefits']}\n"

    prompt_template += f'\n질문: {content}'
    return prompt_template


class QAService:
    """질의응답(QA) 서비스 관리 클래스."""

    def __init__(self, db_directory: str, model_name="gpt-3.5-turbo-0125", temperature=0.1, max_tokens=3500):
        self.db_directory = db_directory
        self.embedding = OpenAIEmbeddings()
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=0.5,
            frequency_penalty=0.5
        )
        self.output_parser = StrOutputParser()
        # 벡터 데이터베이스 로드
        self.vectordb = Chroma(persist_directory=self.db_directory, embedding_function=self.embedding).as_retriever()

    def retrieve_relevant_text(self, content: str, num_results: int = 3) -> str:
        """벡터 데이터베이스에서 관련 문서를 검색하여 반환"""
        results = self.vectordb.get_relevant_documents(content)
        # 검색된 텍스트들을 연결하여 반환
        relevant_texts = "\n".join([res.page_content for res in results[:num_results]])
        return relevant_texts

    def qacall(self, category: str, content: str, extra_data: dict):
        """질의응답 실행"""

        # 벡터 DB에서 관련 문서 검색
        relevant_text = self.retrieve_relevant_text(content)

        # 검색된 내용을 바탕으로 프롬프트 생성
        prompt_text = create_prompt(category, content, extra_data, relevant_text)
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text)
        ])

        # 체인 생성: 프롬프트 -> LLM -> 파서
        qa_chain = prompt | self.llm | self.output_parser

        # 체인을 통해 LLM 응답 생성
        with get_openai_callback() as cb:
            llm_response = qa_chain.invoke({"user_input": content})

        # 응답 및 토큰 사용량 정보 반환
        return llm_response

