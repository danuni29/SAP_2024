from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

app = Flask(__name__, template_folder='templates')

def get_region_code(region):
    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrdlInfo/getWeatherZoneCodeList'
    serviceKey = '53nPttwPfL8c+MibSBVTGOgXVMg1j/e5ZJnIwktQE4QfnL+Xcry61/sqyvhiRRMqZuh1WaEE7HYR54FalGkFwg=='

    params = {
        'serviceKey': serviceKey,
        'pageNo': '1',
        'numOfRows': '100',
    }

    try:
        response = requests.get(url, params=params)
        decoded_content = unquote(response.content.decode("utf-8"))

        root = ET.fromstring(decoded_content)
        for zone in root.findall('.//item'):
            zone_spot_list = zone.find('zone_Spot_List')
            if zone_spot_list is not None:
                for spot in zone_spot_list.findall('.//item'):
                    spot_name = spot.find('obsr_Spot_Nm').text
                    spot_code = spot.find('obsr_Spot_Code').text
                    spot_code = spot.find('obsr_Spot_Code').text

                    if spot_name == region:
                        return spot_code

        return f"'{region}'에 해당하는 코드를 찾을 수 없습니다."
    except requests.exceptions.RequestException as e:
        return f"API 요청에 실패했습니다: {e}"

def get_GDD(region, begin_date, end_date, crop_name="일반작물", base_temp='5.0'):
    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrwDay/getWeatherDegreeDaySpotList'
    serviceKey = '53nPttwPfL8c+MibSBVTGOgXVMg1j/e5ZJnIwktQE4QfnL+Xcry61/sqyvhiRRMqZuh1WaEE7HYR54FalGkFwg=='

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

    params = {
        'serviceKey': serviceKey,
        'obsr_Spot_Code': get_region_code(region),
        'begin_Date': begin_date,
        'end_Date': end_date,
        'growth_Temp_Crop_Code': crop_data[crop_name]["crop_code"],
        'growth_Temp': crop_data[crop_name]["생장개시온도"]
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        decoded_content = unquote(response.content.decode("utf-8"))
        print(decoded_content)

        root = ET.fromstring(response.content)
        # five_gdd_list = []
        gdd_list = []

        for each_item in root.findall('.//items/item'):
            # five_gdd = each_item.find('five_Growth_Degree_Day').text
            gdd = each_item.find('growth_Degree_Day').text
            # five_gdd_list.append(five_gdd)
            gdd_list.append(gdd)

        return gdd_list

    except requests.exceptions.RequestException as e:
        return f"API 요청 중 오류가 발생했습니다: {e}"
    except ET.ParseError:
        return "XML 파싱 중 오류가 발생했습니다."


def get_average_GDD(region, begin_date, end_date, crop_name="일반작물"):
    # Define the base URL and API key
    url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/GrwDay/getWeatherDegreeDaySpotList'
    serviceKey = '53nPttwPfL8c+MibSBVTGOgXVMg1j/e5ZJnIwktQE4QfnL+Xcry61/sqyvhiRRMqZuh1WaEE7HYR54FalGkFwg=='

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

    crop_code = crop_data[crop_name]["crop_code"]
    base_temp = crop_data[crop_name]["생장개시온도"]

    begin_date_obj = datetime.strptime(begin_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    num_days = (end_date_obj - begin_date_obj).days + 1
    total_gdd_sums = [0] * num_days
    valid_years = 5

    # Loop through the last 5 years to collect GDD data
    for year_offset in range(1, valid_years + 1):
        year = begin_date_obj.year - year_offset
        past_begin_date = f"{year}-{begin_date_obj.month:02d}-{begin_date_obj.day:02d}"
        past_end_date = (datetime.strptime(past_begin_date, "%Y-%m-%d") + timedelta(days=num_days - 1)).strftime(
            "%Y-%m-%d")

        params = {
            'serviceKey': serviceKey,
            'obsr_Spot_Code': get_region_code(region),
            'begin_Date': past_begin_date,
            'end_Date': past_end_date,
            'growth_Temp_Crop_Code': crop_code,
            'growth_Temp': base_temp
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            decoded_content = unquote(response.content.decode("utf-8"))
            root = ET.fromstring(decoded_content)

            # Collect the GDD for each day
            for idx, each_item in enumerate(root.findall('.//items/item')):
                gdd = float(each_item.find('growth_Degree_Day').text)
                total_gdd_sums[idx] += gdd

        except requests.exceptions.RequestException as e:
            return f"API 요청 중 오류가 발생했습니다: {e}"
        except ET.ParseError:
            return "XML 파싱 중 오류가 발생했습니다."

    avg_gdd_list = [round(total / valid_years, 3) for total in total_gdd_sums]

    return avg_gdd_list

@app.route('/')
def index():
    return render_template('index.html')
# region = '가평군 가평읍'
# print(f"5 year average: {get_average_GDD(region, '2022-09-01', '2022-09-10', '옥수수')}")
@app.route('/get_gdd', methods=['GET'])
def get_gdd():
    region = request.args.get('region')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    crop_type = request.args.get('cropType', default="일반작물")

    print(f"Region: {region}, Start Date: {start_date}, End Date: {end_date}, Crop Type: {crop_type}")

    gdd_list = get_GDD(region, start_date, end_date, crop_type)
    five_gdd_list = get_average_GDD(region, start_date, end_date, crop_type)

    print(f"GDD 5-Day: {five_gdd_list}")
    print(f"GDD Total: {gdd_list}")

    if five_gdd_list is not None and gdd_list is not None:
        return jsonify({
            'gdd_five_day': five_gdd_list,
            'gdd_total': gdd_list
        })


    else:
        return jsonify({'error': 'GDD 계산에 실패했습니다.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
