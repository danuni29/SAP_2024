import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import os
import geopandas as gpd
import folium
from folium import Choropleth
from streamlit_folium import st_folium

gdf = gpd.read_file(r'C:\code\SAP_2024\02_Model\sigungu_map\sig.shp')
print(gdf.columns)
# 좌표 체계가 설정되어 있는지 확인
if gdf.crs is None:
    # CRS가 설정되지 않은 경우, 수동으로 EPSG:5174를 설정 (예: 한국의 TM 좌표계)
    gdf = gdf.set_crs(epsg=5174)

# 좌표계를 EPSG:4326 (WGS84)로 변환
gdf = gdf.to_crs(epsg=4326)

# 예시 데이터 (각 지역별 통계 예: 인구 수)
# data.csv: location(지역 코드 또는 이름)과 value(통계 값) 포함
data = pd.read_csv(r'C:\code\SAP_2024\02_Model\sigungu_map\data.csv')  # 예시: 각 지역별 통계 데이터

# 지도 생성 (대한민국 중심으로 설정)
m = folium.Map(location=[36.5, 127.5], tiles='cartodbpositron', zoom_start=7)

gdf['SIG_CD'] = gdf['SIG_CD'].astype(str)
data['location'] = data['location'].astype(str)

# Choropleth 지도 추가
Choropleth(
    geo_data=gdf,  # GeoDataFrame 자체를 사용
    data=data,  # 시각화할 데이터
    columns=['location', 'value'],  # 데이터의 지역 코드 또는 이름, 값
    key_on='feature.properties.SIG_CD',  # GeoDataFrame에서 실제 존재하는 'SIG_CD' 열 사용
    fill_color='YlGnBu',  # 색상 스케일
    legend_name='Population',  # 범례 이름
).add_to(m)

# Streamlit 앱에서 지도 표시
st.title("전국 행정구역별 인구 수 Choropleth 지도")

# Folium 지도를 Streamlit에서 렌더링
st_folium(m, width=725)