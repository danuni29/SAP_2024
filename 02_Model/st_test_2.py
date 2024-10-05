import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
import streamlit as st

# CSV 파일 읽기
csv_file = r'C:\code\SAP_2024\02_Model\Pear_Model_output\CD_Model_result_나주.csv'
flowering_data = pd.read_csv(csv_file)

# 날짜 데이터를 Month-Day 형식으로 변환 및 문자열로 유지
flowering_data['full_bloom_date'] = pd.to_datetime(flowering_data['full_bloom_date'])
flowering_data['bloom_day'] = flowering_data['full_bloom_date'].dt.strftime('%m-%d')

# 날짜를 카테고리화하여 고유 코드로 변환
flowering_data['bloom_day_code'] = flowering_data['bloom_day'].astype('category').cat.codes

# 2. 전국 시도 경계선을 포함한 Shapefile 불러오기
gdf_boundary = gpd.read_file(r'C:\code\SAP_2024\02_Model\sigungu_map\sig.shp', encoding='cp949')
gdf_boundary['SIG_KOR_NM'] = gdf_boundary['SIG_KOR_NM'].str[:2]


# 3. 데이터 병합
def merge_data(flowering_data, gdf_boundary, year):
    # '나주시'를 지역으로 설정
    flowering_data['region'] = '나주시'

    # 병합
    kr_gpd = pd.merge(gdf_boundary, flowering_data[flowering_data['year'] == year], left_on='SIG_KOR_NM',
                      right_on='region', how='left')

    # 결측치 처리 (병합 후 값이 없으면 0 또는 기타 값으로 대체)
    kr_gpd['bloom_day_code'].fillna(0, inplace=True)

    return kr_gpd


# 4. 지도 그리기 함수
def plot_flowering_map(df, year, model):
    lst = [year - i for i in range(4, -1, -1)]

    # 병합한 GeoDataFrame 생성
    kr_gpd = merge_data(df, gdf_boundary, year)

    # 범위 설정
    date_vmin = kr_gpd[model].min()
    date_vmax = kr_gpd[model].max()

    fig, axes = plt.subplots(1, 5, figsize=(25, 6))
    divider = make_axes_locatable(axes[-1])
    cax = divider.append_axes("right", size="5%", pad=0.5)

    model_column = model
    for i, y in enumerate(lst):
        kr_gpd = merge_data(df, gdf_boundary, y)  # 연도별 데이터 병합
        kr_gpd.plot(column=model_column, ax=axes[i], legend=False, cmap='rainbow',
                    missing_kwds={'color': 'gray'}, vmin=date_vmin, vmax=date_vmax)

    # 마지막 서브플롯에 색상바 추가
    kr_gpd.plot(column=model_column, ax=axes[-1], legend=True, cax=cax, cmap='rainbow',
                missing_kwds={'color': 'gray'}, vmin=date_vmin, vmax=date_vmax)

    # 날짜 포맷 변경 (fromordinal 대신 bloom_day 값을 사용)
    formatter = ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(False)
    cax.yaxis.set_major_formatter(formatter)

    # bloom_day_code와 원래 bloom_day 값 매핑
    bloom_day_mapping = dict(enumerate(flowering_data['bloom_day'].astype('category').cat.categories))

    # y 축 눈금 매핑
    ticks = cax.get_yticks()
    cax.set_yticklabels([bloom_day_mapping.get(int(tick), '') for tick in ticks])

    for i, ax in enumerate(axes):
        ax.set_title(f"{lst[i]}년 만개일")
        ax.set_axis_off()

    # Streamlit에서 그래프를 표시하도록 plt.show() 대신 사용
    st.pyplot(fig)


# Streamlit UI (이 코드를 Streamlit 환경에서 실행할 때 사용)
st.title("만개일 시각화 (나주시)")

year = 2024
model = 'bloom_day_code'  # bloom_day_code를 사용하여 숫자 값으로 처리

# 지도 표시 버튼
if st.button("지도 표시"):
    plot_flowering_map(flowering_data, year, model)
