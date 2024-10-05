import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import streamlit as st
import matplotlib.font_manager as fm


# 1. CSV 파일에서 데이터를 읽어오기
def load_data_for_year(year, folder_path):
    data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            # 파일 이름에서 지역 추출 (예: CD_Model_result_나주.csv -> 나주)
            region = file_name.replace('CD_Model_result_', '').replace('.csv', '')

            # CSV 파일 읽기
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)

            # 연도별 데이터 필터링
            df_year = df[df['year'] == year]

            # 날짜 데이터를 'bloom_day'로 변환 (예: 'full_bloom_date' 또는 유사한 열을 사용)
            if 'full_bloom_date' in df_year.columns:
                df_year['full_bloom_date'] = pd.to_datetime(df_year['full_bloom_date'], errors='coerce')  # 에러 무시 옵션 추가
                df_year['bloom_day'] = df_year['full_bloom_date'].dt.strftime('%m-%d')

            # 지역 추가
            df_year['region'] = region

            # 데이터 수집
            data.append(df_year)

    # 모든 지역 데이터를 하나의 데이터프레임으로 병합
    all_data = pd.concat(data, ignore_index=True)

    return all_data


# 2. 전국 시도 경계선을 포함한 Shapefile 불러오기
def load_boundary_data(shapefile_path):
    gdf_boundary = gpd.read_file(shapefile_path, encoding='cp949')
    gdf_boundary['SIG_KOR_NM'] = gdf_boundary['SIG_KOR_NM'].str[:2]  # 시도 이름만 사용
    return gdf_boundary


# 3. 병합 및 지도 시각화 함수
def plot_flowering_map(all_data, gdf_boundary, year):
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 지역별 데이터를 지도 경계 데이터와 병합 (how='outer'로 설정하여 모든 지역 표시)
    gdf_boundary = gdf_boundary.rename(columns={'SIG_KOR_NM': 'region'})  # 지역명과 일치시키기
    kr_gpd = pd.merge(gdf_boundary, all_data, on='region', how='outer')

    # 결측값 제거 (bloom_day 없는 지역 제거)
    kr_gpd = kr_gpd.dropna(subset=['bloom_day'])

    # bloom_day를 숫자로 변환하여 색상 범위로 사용
    kr_gpd['bloom_day_numeric'] = kr_gpd['bloom_day_numeric'].apply(lambda x: int(x) if pd.notnull(x) else None)
    kr_gpd = kr_gpd.dropna(subset=['bloom_day_numeric'])
    kr_gpd['bloom_day_numeric'] = pd.to_numeric(kr_gpd['bloom_day_numeric'], errors='coerce')

    # 결측값 제거 후 시각화할 컬럼의 범위 설정 (날짜를 숫자로 변환한 값의 최소, 최대값)
    date_vmin = kr_gpd['bloom_day_numeric'].min()
    date_vmax = kr_gpd['bloom_day_numeric'].max()

    # 지도 그리기
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    # 기본 배경은 회색으로 설정
    gdf_boundary.plot(ax=ax, color='lightgray', edgecolor='black')

    # bloom_day가 있는 데이터만 색상 표시
    kr_gpd.dropna(subset=['bloom_day_numeric']).plot(column='bloom_day_numeric', ax=ax, legend=False, cmap='rainbow',
                                                     missing_kwds={'color': 'gray'}, vmin=date_vmin, vmax=date_vmax)

    # 타이틀 설정
    ax.set_title(f"{year}년 만개일 지도", fontsize=15)
    ax.set_axis_off()

    # 컬러바 추가
    sm = plt.cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=date_vmin, vmax=date_vmax))
    cbar = fig.colorbar(sm, cax=cax)

    # 컬러바의 날짜 눈금 표시
    ticks = cbar.get_ticks()  # 컬러바 눈금 가져오기
    tick_labels = [pd.Timestamp.fromordinal(int(tick)).strftime('%m-%d') for tick in ticks]
    cbar.set_ticks([int(tick) for tick in ticks])  # float -> int로 변환
    cbar.set_ticklabels(tick_labels)  # 컬러바에 날짜 표시

    # 컬러바 레이블 설정
    cbar.set_label('만개일 (MM-DD)')

    # Streamlit에 지도 표시
    st.pyplot(fig)


# 4. Streamlit 앱 실행
def main():
    # Streamlit UI 설정
    st.title("연도별 만개일 지도")

    # 연도 입력 받기
    year = st.number_input("연도를 입력하세요", min_value=2004, max_value=2024, value=2024)

    # 지도 표시 버튼
    if st.button("지도 표시"):
        # CD_Model 폴더에서 연도별 데이터 로드
        folder_path = r'C:\code\SAP_2024\02_Model\Pear_Model_output\CD_Model'  # CD_Model 폴더 경로
        all_data = load_data_for_year(year, folder_path)

        # 시도 경계선 로드
        shapefile_path = r'C:\code\SAP_2024\02_Model\sigungu_map\sig.shp'  # Shapefile 경로
        gdf_boundary = load_boundary_data(shapefile_path)

        # 지도 그리기
        plot_flowering_map(all_data, gdf_boundary, year)


# Streamlit 앱 시작
if __name__ == '__main__':
    main()
