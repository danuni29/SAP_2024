import uvicorn
from fastapi import FastAPI, Request
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
app = FastAPI()


def get_region_code(region):
    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrdlInfo/getWeatherZoneCodeList'
    serviceKey = 'CaNVjajLQjjwRIQMs8QNBr1uV86t3KkH5FT8sbOTcWIpZOyWUZ9VdEze/miJwopWCi4M4ayJAUAnXbTeogRGdA=='

    params = {
        'serviceKey': serviceKey,
        'pageNo': '1',
        'numOfRows': '100',
    }

    try:

        response = requests.get(url, params=params)
        decoded_content = unquote(response.content.decode("utf-8"))
        print(decoded_content)

        # XML 데이터를 파싱
        root = ET.fromstring(decoded_content)

        # 지역명에 따른 코드 찾기
        for zone in root.findall('.//item'):
            zone_spot_list = zone.find('zone_Spot_List')

            if zone_spot_list is not None:
                for spot in zone_spot_list.findall('.//item'):
                    spot_name = spot.find('obsr_Spot_Nm').text  # obsr_Spot_Nm 추출
                    spot_code = spot.find('obsr_Spot_Code').text  # obsr_Spot_Code 추출

                    if spot_name == region:
                        return spot_code

        # 해당 지역명을 찾지 못한 경우
        return f"'{region}'에 해당하는 코드를 찾을 수 없습니다."


    except requests.exceptions.RequestException as e:
        return f"API 요청에 실패했습니다: {e}"


def get_GDD(region, begin_date, end_date, crop_name="일반작물", base_temp='5.0'):

    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrwDay/getWeatherDegreeDaySpotList'
    serviceKey = 'CaNVjajLQjjwRIQMs8QNBr1uV86t3KkH5FT8sbOTcWIpZOyWUZ9VdEze/miJwopWCi4M4ayJAUAnXbTeogRGdA=='

    crop_data = {
        "겨자": {"crop_code": "01", "생장개시온도": 0.0},
        "시금치": {"crop_code": "02", "생장개시온도": 2.2},
        "상추": {"crop_code": "03", "생장개시온도": 4.4},
        "보리": {"crop_code": "04", "생장개시온도": 5.0},
        "완두": {"crop_code": "05", "생장개시온도": 5.5},
        "아스파라거스": {"crop_code": "06", "생장개시온도": 5.5},
        "옥수수": {"crop_code": "07", "생장개시온도": 10.0},
        "콩": {"crop_code": "08", "생장개시온도": 10.0},
        "토마토": {"crop_code": "09", "생장개시온도": 13.0},
        "호박": {"crop_code": "10", "생장개시온도": 13.0},
        "벼": {"crop_code": "11", "생장개시온도": 15.0},
        "일반작물": {"crop_code": "12", "생장개시온도": 5.0},
        "직접입력": {"crop_code": "99", "생장개시온도": None}
    }


    params = {'serviceKey': serviceKey,
              'obsr_Spot_Code': get_region_code(region),
              'begin_Date': begin_date,
              'end_Date': end_date,
              'growth_Temp_Crop_Code': crop_data[crop_name]["crop_code"],
              'growth_Temp': crop_data[crop_name]["생장개시온도"]}


    try:
        # API 요청
        response = requests.get(url, params=params)

        response.raise_for_status()  # 요청 성공 여부 확인
        decoded_content = unquote(response.content.decode("utf-8"))
        print(decoded_content)

        root = ET.fromstring(response.content)

        # 결과에서 GDD 데이터를 추출
        five_gdd_list = []
        gdd_list = []

        for each_item in root.findall('.//items/item'):
            five_gdd = each_item.find('five_Growth_Degree_Day').text
            gdd = each_item.find('growth_Degree_Day').text
            five_gdd_list.append(five_gdd)
            gdd_list.append(gdd)

        return five_gdd_list, gdd_list


    except requests.exceptions.RequestException as e:
        return f"API 요청 중 오류가 발생했습니다: {e}"
    except ET.ParseError:
        return "XML 파싱 중 오류가 발생했습니다."



# print(get_region_code())
# print(get_GDD('가평군 가평읍', '2019-03-01', '2019-03-29'))

@app.get("/get_gdd/{region}/{begin_date}/{end_date}/{crop_code}/{base_temp}")

def index():
    pass

@app.get("/get_gdd")
async def test(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
