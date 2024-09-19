import uvicorn
from fastapi import FastAPI
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

app = FastAPI()


def get_region_code(region):
    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrdlInfo/getWeatherZoneCodeList'
    serviceKey = 'CaNVjajLQjjwRIQMs8QNBr1uV86t3KkH5FT8sbOTcWIpZOyWUZ9VdEze/miJwopWCi4M4ayJAUAnXbTeogRGdA=='  # 공공데이터포털에서 발급받은 서비스 키를 입력하세요.

    params = {
        'serviceKey': serviceKey,  # API 키
        'pageNo': '1',  # 페이지 번호
        'numOfRows': '100',  # 한 번에 불러올 데이터의 개수
    }


    # API 요청
    response = requests.get(url, params=params)
    decoded_content = unquote(response.content.decode("utf-8"))
    print(decoded_content)

    # XML 데이터를 파싱
    root = ET.fromstring(decoded_content)

    # 지역명에 따른 코드 찾기
    for item in root.findall('.//item'):
        name = item.find('zone_Name').text  # 지역명
        code = item.find('zone_Code').text  # 지역 코드
        if name == region:
            return code

    # 해당 지역명을 찾지 못한 경우
    return f"지역명 '{region}'에 해당하는 코드를 찾을 수 없습니다."

def main():

    zone_code = get_region_code('태백고랭')
    print(f"지역 코드: {zone_code}")

if __name__ == "__main__":
    main()

