import requests

# KAMIS API 기본 URL
api_url = "http://www.kamis.or.kr/service/price/xml.do?action=periodProductList"

# API 요청에 필요한 파라미터 설정
params = {
    'p_cert_key': '8f10b9ce-54cf-42d7-ac93-8dc87e3257a3',  # 인증키 입력
    'p_cert_id': '01089144423',        # ID 입력
    'p_returntype': 'xml',         # 응답 형식 (xml 또는 json)
    'p_startday': '2023-01-01',    # 시작 날짜
    'p_endday': '2023-01-10',      # 종료 날짜
    'p_productclscode': '01',      # 품목 구분 코드 (01: 채소류, 02: 과일류 등)
    'p_itemcategorycode': '100',   # 품목 코드 (예: 100: 배추, 200: 무)
    'p_countrycode': '1101',       # 국가 코드 (1101: 서울)
    'p_convert_kg_yn': 'Y',        # kg 단위 변환 여부
}

# API 요청
response = requests.get(api_url, params=params)

# 응답 상태 코드 확인
if response.status_code == 200:
    # 응답 데이터를 텍스트로 출력 (원본 XML 데이터 확인)
    print(response.text)
else:
    print(f"Error: {response.status_code}")
