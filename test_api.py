import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트할 서버 URL
base_url = "http://localhost:5000"

# 테스트할 질문 ID
question_id = 10

# 테스트할 Authorization 토큰
access_token = "eyJ0eXAiOiJKV1QiLCJhbGc"

# 테스트할 요청 데이터
request_data = {
    "id": 10,
    "content": "질문 내용",
    "category": "노하우",
    "extraData": {
        "bossType": "STORE_OWNER",
        "businessType": "건강식 전문점",
        "location": "서울 서초구",
        "customerType": "30~50대 직장인",
        "storeInfo": "월매출 2500",
        "budget": "10만"
    }
}

def test_api():
    try:
        # API 엔드포인트 URL
        url = f"{base_url}/{question_id}/answers"
        
        # 요청 헤더
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Sending request to: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Request data: {request_data}")
        
        # POST 요청 보내기
        response = requests.post(url, headers=headers, json=request_data)
        
        # 응답 출력
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        
        # 응답 본문 출력 시도
        try:
            response_json = response.json()
            logger.info(f"Response JSON: {response_json}")
        except requests.exceptions.JSONDecodeError:
            logger.info(f"Response Text: {response.text}")
            
        # 상태 코드 확인
        response.raise_for_status()
        
    except requests.exceptions.ConnectionError:
        logger.error("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        logger.error("요청 시간이 초과되었습니다.")
    except requests.exceptions.RequestException as e:
        logger.error(f"요청 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    test_api()