import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import chardet
# import numpy as np
def get_bloom_date(datalist, select_year):
    """
    datalist에서 선택한 연도의 full_bloom_date만 필터링하여 출력하는 함수
    """
    result = {}
    for model_data in datalist:
        model_name, data = model_data  # 모델 이름과 데이터 프레임을 언패킹
        data['year'] = data['full_bloom_date'].dt.year  # 날짜에서 연도 추출
        # 선택한 연도에 해당하는 데이터를 필터링
        bloom_date = data[data['year'] == select_year]['full_bloom_date']

        if not bloom_date.empty:
            result[model_name] = bloom_date.dt.strftime('%Y-%m-%d').values[0]  # 날짜 형식을 YYYY-MM-DD로 변환

    return result
def load_model_data(select_models, select_region, select_species, select_variety=None):
    """
    선택된 모델, 지역, 품종에 따라 데이터를 로드하고 예측일을 추출하는 함수 (전체 연도를 포함)
    """
    data_list = []
    variety_dict = {
        '유명': 'ymn',
        '창방조생': 'cbj',
        '천중도백도': 'cjo',
        '장호원백도': 'jhw',
        '청홍': 'chh'
    }

    for model in select_models:
        # 모델별로 파일 경로 생성
        if select_species == '배🍐':
            file_path = rf"C:\code\SAP_2024\02_Model\Pear_Model_output\{model}_Model\{model}_Model_result_{select_region}.csv"
        elif select_species == '복숭아🍑':
            # 각 모델에 대해 개별적으로 경로 생성
            file_path = rf"C:\code\SAP_2024\02_Model\Peach_Model\Peach_Model_output\{model}_Model\{select_region}_{variety_dict[select_variety]}_{model}.csv"
            print(file_path)

        # 파일 읽기 및 데이터 처리
        if os.path.exists(file_path):
            model_data = pd.read_csv(file_path)
            model_data['full_bloom_date'] = pd.to_datetime(model_data['full_bloom_date'])
            data_list.append((model, model_data))
        else:
            st.write(f"{model} 모델에 대한 파일을 찾을 수 없습니다: {file_path}")

    # return을 반복문 밖으로 이동
    return data_list


import matplotlib.dates as mdates

import matplotlib.dates as mdates

def plot_avg_temperature(data_path, select_year, select_region):
    """
    이 함수는 지정된 경로에서 선택한 지역의 파일을 필터링하여 읽어들인 후,
    선택한 연도와 나머지 19개의 평년 데이터를 기반으로 오차범위를 포함한 그래프와
    선택한 연도를 선으로 표시하는 그래프를 그린다.

    Parameters:
    data_path (str): 데이터 파일이 있는 경로
    select_year (int): 비교할 연도 (2004년부터 2024년까지 중 선택)
    select_region (str): 지역 이름 (폴더나 파일 이름에 포함된 문자열)

    Returns:
    None: Streamlit을 통해 그래프를 출력
    """
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    # Step 1: Read all files in the folder that contain the selected region in the name
    all_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if
                 os.path.isfile(os.path.join(data_path, f)) and select_region in f]

    # If no files are found, create an empty DataFrame
    if not all_files:
        weather_data = pd.DataFrame(columns=['year', 'month', 'day', 'tavg'])
    else:
        # Step 2: Combine all files into a single DataFrame
        df_list = [pd.read_csv(file) for file in all_files]
        weather_data = pd.concat(df_list, ignore_index=True)

    # Step 3: Create 'date' column from 'year', 'month', and 'day' columns
    if not weather_data.empty:
        # tavg 컬럼을 숫자로 변환
        weather_data['tavg'] = pd.to_numeric(weather_data['tavg'], errors='coerce')
        weather_data = weather_data.dropna(subset=['tavg'])

        # 날짜 변환
        weather_data['date'] = pd.to_datetime(weather_data[['year', 'month', 'day']], errors='coerce')

        # Step 4: Preprocessing
        weather_data['year'] = weather_data['date'].dt.year
        weather_data['month_day'] = weather_data['date'].dt.strftime('%m-%d')  # Use MM-DD format for X-axis
        weather_data = weather_data[
            (weather_data['date'].dt.month >= 1) & (weather_data['date'].dt.month <= 5)]  # Filter for Jan to May

        # Separate data for 평년 and selected year
        normal_years_data = weather_data[weather_data['year'] != select_year]
        selected_year_data = weather_data[weather_data['year'] == select_year]

        # Step 5: Calculate the max and min values for 평년 (normal years)
        normal_grouped = normal_years_data.groupby('date').agg({'tavg': ['max', 'min']}).reset_index()
        normal_grouped.columns = ['date', 'max_tavg', 'min_tavg']

        # Step 6: Group selected year data by date and calculate the mean temperature
        selected_grouped = selected_year_data.groupby('date').agg({'tavg': 'mean'}).reset_index()

        # Step 7: Plotting with Matplotlib
        plt.figure(figsize=(10, 6))

        # 날짜 데이터를 숫자로 변환
        normal_grouped['date'] = mdates.date2num(normal_grouped['date'])
        selected_grouped['date'] = mdates.date2num(selected_grouped['date'])

        # NaN 값을 체크하고 제거
        if normal_grouped[['max_tavg', 'min_tavg']].isnull().values.any():
            normal_grouped = normal_grouped.dropna(subset=['max_tavg', 'min_tavg'])

        # Plot the mean temperature line for 평년 with a shaded band (max-min range)
        plt.plot(normal_grouped['date'], (normal_grouped['max_tavg'] + normal_grouped['min_tavg']) / 2,
                 color='orange', label='평년')
        plt.fill_between(
            normal_grouped['date'],
            normal_grouped['min_tavg'],
            normal_grouped['max_tavg'],
            color='gray', alpha=0.3, label='온도 범위 (최대-최소)'
        )

        # Plot the line for the selected year
        plt.plot(selected_grouped['date'], selected_grouped['tavg'], color='blue', label=f'{select_year}년')

        # Customizing X-axis to show dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

        plt.xlabel('Date (MM-DD)')
        plt.ylabel('Temperature (°C)')
        plt.title(f'{select_region} 지역 - {select_year}년 일평균 기온 그래프')
        plt.legend(loc='upper left')

        # Step 8: Show the plot in Streamlit using matplotlib
        st.pyplot(plt)

    else:
        st.write(f"선택한 지역 '{select_region}'에 해당하는 데이터가 없습니다.")
        return


def load_data_for_year(year, folder_path):
    data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            # 파일 이름에서 지역 추출 (예: CD_Model_result_나주.csv -> 나주)
            region = file_name.replace('CD_Model_result_', '').replace('.csv', '')

            # CSV 파일 읽기
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)

            df['full_bloom_date'] = pd.to_datetime(df['full_bloom_date'])  # 날짜 형식 변환
            df_year = df[df['full_bloom_date'].dt.year == year]

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

    # bloom_day를 숫자로 변환하여 색상 범위로 사용 (NaT 처리 포함)
    kr_gpd['bloom_day_numeric'] = pd.to_datetime(kr_gpd['bloom_day'], format='%m-%d', errors='coerce').apply(
        lambda x: x.toordinal() if pd.notnull(x) else None)

    # 변환 후 남아있는 결측값을 제거하고 정수형으로 변환
    kr_gpd = kr_gpd.dropna(subset=['bloom_day_numeric'])  # NaN 제거
    kr_gpd['bloom_day_numeric'] = kr_gpd['bloom_day_numeric'].astype(int)  # float -> int 변환

    date_vmin = kr_gpd['bloom_day_numeric'].min()
    date_vmax = kr_gpd['bloom_day_numeric'].max()

    # 지도 그리기
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    # 기본 배경은 회색으로 설정
    gdf_boundary.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)

    # bloom_day가 있는 데이터만 색상 표시
    kr_gpd.plot(column='bloom_day_numeric', ax=ax, legend=False, cmap='rainbow',
                missing_kwds={'color': 'gray'}, vmin=date_vmin, vmax=date_vmax)

    # 타이틀 설정
    ax.set_title(f"{year}년 예측 만개일 지도", fontsize=15)
    ax.set_axis_off()

    # 컬러바 추가
    sm = plt.cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=date_vmin, vmax=date_vmax))
    cbar = fig.colorbar(sm, cax=cax)

    # 컬러바의 날짜 눈금 표시
    ticks = cbar.get_ticks()  # 컬러바 눈금 가져오기
    tick_labels = [pd.Timestamp.fromordinal(int(tick)).strftime('%m-%d') for tick in ticks if not pd.isnull(tick)]
    cbar.set_ticks([int(tick) for tick in ticks if not pd.isnull(tick)])  # float -> int로 변환
    cbar.set_ticklabels(tick_labels)  # 컬러바에 날짜 표시

    # 컬러바 레이블 설정
    cbar.set_label('만개일 (MM-DD)')

    # Streamlit에 지도 표시
    st.pyplot(fig)

def draw_bloom_date_graph(data_list, observed_data, select_region):
    """
    예측된 개화일을 그래프로 그리는 함수 (전체 연도를 포함)
    """
    fig = go.Figure()

    # 여러 모델에 대해 데이터를 그리기
    for model, data in data_list:
        if not data.empty:
            data['year'] = data['full_bloom_date'].dt.year
            data['bloom_day'] = pd.to_datetime(data['full_bloom_date'].dt.strftime('2000-%m-%d'))

            # 전체 연도 데이터를 그리기
            fig.add_trace(go.Scatter(x=data['year'], y=data['bloom_day'],
                                     mode='lines+markers', name=f'{model} 예측일'))

    # 관측된 개화일 데이터가 있을 때
    if observed_data is not None:
        observed_data['Date'] = pd.to_datetime(observed_data['Date'])
        observed_data['year'] = observed_data['Date'].dt.year
        observed_data['bloom_day'] = pd.to_datetime(observed_data['Date'].dt.strftime('2000-%m-%d'))

        fig.add_trace(go.Scatter(x=observed_data['year'], y=observed_data['bloom_day'],
                                 mode='lines+markers', name='실제 관측일'))

    # 그래프 레이아웃 설정
    fig.update_layout(
        title=f"Full Bloom Dates in {select_region} (2004-2024)",
        xaxis_title="Year",
        yaxis_title="Full Bloom Date",
        xaxis=dict(type='category'),  # 연도별로 나열
        yaxis=dict(tickformat='%m-%d'),  # y축을 월-일 형식으로 표시
        legend_title="Type",
        hovermode="x unified"
    )

    st.plotly_chart(fig)




def main():
    st.title('2024 스마트농업프로그래밍')
    st.sidebar.title('개화 시기 예측 모델🌸')

    # 작물 선택
    select_species = st.sidebar.selectbox(
        '작물을 선택하세요',
        ['배🍐', '복숭아🍑']
    )

    # 복숭아를 선택했을 때 품종 선택
    if select_species == '복숭아🍑':
        select_variety = st.sidebar.selectbox(
            '품종을 선택하세요',
            ['유명', '창방조생', '천중도백도', '장호원백도', '청홍']
        )

        # 품종에 따른 지역 선택
        if select_variety == '청홍':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['춘천', '수원', '청주', '나주', '진주']
            )
        elif select_variety == '유명':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['춘천', '수원', '청주', '청도', '나주', '진주']
            )
        elif select_variety == '창방조생':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['수원']
            )
        elif select_variety == '장호원백도':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['청도']
            )
        elif select_variety == '천중도백도':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['청도']
            )

    # 배를 선택했을 때 지역 선택
    elif select_species == '배🍐':
        select_region = st.sidebar.selectbox(
            '지역을 선택하세요',
            ['이천', '천안', '상주', '영천', '완주', '나주', '사천', '울주']
        )

    # 연도 선택 (2004~2024)
    select_year = st.sidebar.slider('연도를 선택하세요', 2004, 2024, 2024)


    # 그래프 보기 체크박스
    st.sidebar.write("보고 싶은 그래프를 선택하세요:")
    show_temp = st.sidebar.checkbox('평균온도변화')
    # show_precip = st.sidebar.checkbox('강수량변화')
    show_bloom = st.sidebar.checkbox('개화일변화')

    # 메인 타이틀
    st.title(f"{select_species} 개화 예측 모델")

    if select_species == '배🍐':
        select_model = st.multiselect(
            '사용할 모델을 선택하세요',
            ['DVR', 'mDVR', 'CD']  # 배에 해당하는 모델들
        )
    elif select_species == '복숭아🍑':
        select_model = st.multiselect(
            '사용할 모델을 선택하세요',
            ['DVR', 'CD', 'NCD']  # 복숭아에 해당하는 모델들
        )



    # 여기서부터 이제 결과 표시~~~~

    if select_species == '배🍐':
        data_list = load_model_data(select_model, select_region, select_species)
        # print(data_list)
        bloom_dates = get_bloom_date(data_list, select_year)

        # 결과 출력
        for model, date in bloom_dates.items():
            # print(f"Model: {model}, Full Bloom Date for {select_year}: {date}")
            st.subheader(f"모델: {model}, {select_year}년 예측 만개일: {date}")


        observed_data = pd.read_csv(rf"C:\code\SAP_2024\02_Model\input\observe_data\flowering_date_{select_region}.csv")

        if st.button("지도 표시"):
            if len(select_model) == 1:  # 모델이 하나만 선택된 경우
                model_name = select_model[0]
                folder_path = fr'C:\code\SAP_2024\02_Model\Pear_Model_output\{model_name}_Model'  # CD_Model 폴더 경로
                all_data = load_data_for_year(select_year, folder_path)

                # 시도 경계선 로드
                shapefile_path = r'C:\code\SAP_2024\02_Model\sigungu_map\sig.shp'  # Shapefile 경로
                gdf_boundary = load_boundary_data(shapefile_path)

                # 지도 그리기
                plot_flowering_map(all_data, gdf_boundary, select_year)
            else:
                st.write("하나의 모델만 선택해주세요.")


        # 그래프에 대한 로직은 여기에 추가하면 됩니다.
        if show_temp:
            st.write("평균온도변화 그래프를 표시합니다.")
            # Example usage:
            data_path = r'C:\code\SAP_2024\02_Model\input\weather_data'

            plot_avg_temperature(data_path, select_year, select_region)
            # 그래프 표시 로직 추가
        # if show_precip:
        #     st.write("강수량변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_bloom:
            st.write("개화일변화 그래프를 표시합니다.")
            # draw_bloom_date_graph(predicted_df, observed_data, select_region)
            draw_bloom_date_graph(data_list, observed_data, select_region)

    elif select_species == '복숭아🍑':
        data_list = load_model_data(select_model, select_region, select_species, select_variety)
        # print(data_list)
        bloom_dates = get_bloom_date(data_list, select_year)

        for model, date in bloom_dates.items():
            # print(f"Model: {model}, Full Bloom Date for {select_year}: {date}")
            st.subheader(f"모델: {model}, {select_year}년 예측 만개일: {date}")

        variety_dict = {
            '유명': 'ymn',
            '창방조생': 'cbj',
            '천중도백도': 'cjo',
            '장호원백도': 'jhw',
            '청홍': 'chh'
        }
        # predicted_df = pd.read_csv(rf"C:\code\SAP_2024\02_Model\Peach_Model\Peach_Model_output\{select_region}_{variety_dict[select_variety]}_{select_model}.csv")

        # filtered_data = predicted_df[predicted_df['full_bloom_date'].str[:4] == str(select_year)]
        observed_data_path =rf"C:\code\SAP_2024\02_Model\Peach_Model\peach_observed_data\flowering_date_{select_region}_{variety_dict[select_variety]}.csv"

        # st.subheader(f"{select_region} 지역 {select_year}년 개화일: {filtered_data.iloc[0]['full_bloom_date']}")

        if st.button("지도 표시"):
            if len(select_model) == 1:  # 모델이 하나만 선택된 경우
                model_name = select_model[0]
                folder_path = fr'C:\code\SAP_2024\02_Model\Peach_Model_Output\{model_name}_Model'  # CD_Model 폴더 경로
                all_data = load_data_for_year(select_year, folder_path)


                # 시도 경계선 로드
                shapefile_path = r'C:\code\SAP_2024\02_Model\sigungu_map\sig.shp'  # Shapefile 경로
                gdf_boundary = load_boundary_data(shapefile_path)

                # 지도 그리기
                plot_flowering_map(all_data, gdf_boundary, select_year)
            else:
                st.write("하나의 모델만 선택해주세요.")

        if os.path.exists(observed_data_path):
            observed_data = pd.read_csv(observed_data_path)
        else:
            observed_data = None

        # 그래프에 대한 로직은 여기에 추가하면 됩니다.
        if show_temp:
            st.write("평균온도변화 그래프를 표시합니다.")

            data_path = r'C:\code\SAP_2024\02_Model\input\weather_data'

            plot_avg_temperature(data_path, select_year, select_region)

        # if show_precip:
        #     st.write("강수량변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_bloom:
            st.write("개화일변화 그래프를 표시합니다.")
            # draw_bloom_date_graph(predicted_df, observed_data, select_region)
            draw_bloom_date_graph(data_list, observed_data, select_region)


if __name__ == '__main__':
    main()
