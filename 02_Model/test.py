import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import os


def load_model_data(select_models, select_region, select_species):
    """
    선택된 모델, 지역에 따라 데이터를 로드하고 예측일을 추출하는 함수 (전체 연도를 포함)
    """
    data_list = []
    for model in select_models:
        # 모델별로 파일 경로 생성
        if select_species == '배🍐':
            file_path = rf"C:\code\SAP_2024\02_Model\Pear_Model_output\{model}_Model\{model}_Model_result_{select_region}.csv"
        elif select_species == '복숭아🍑':
            file_path = rf"C:\code\SAP_2024\02_Model\Peach_Model\Peach_Model_output\{select_region}_{model}.csv"

        # 파일 읽기 및 데이터 처리
        if os.path.exists(file_path):
            model_data = pd.read_csv(file_path)
            model_data['full_bloom_date'] = pd.to_datetime(model_data['full_bloom_date'])
            data_list.append((model, model_data))
        else:
            st.write(f"{model} 모델에 대한 파일을 찾을 수 없습니다: {file_path}")

    return data_list


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

    # 작물 선택
    select_species = st.sidebar.selectbox(
        '작물을 선택하세요',
        ['배🍐', '복숭아🍑']
    )

    # 배일 때 지역 선택
    if select_species == '배🍐':
        select_region = st.sidebar.selectbox(
            '지역을 선택하세요',
            ['이천', '천안', '상주', '영천', '완주', '나주', '사천', '울주']
        )

    # 복숭아일 때 지역과 품종 선택
    elif select_species == '복숭아🍑':
        select_variety = st.sidebar.selectbox(
            '품종을 선택하세요',
            ['유명', '창방조생', '천중도백도', '장호원백도', '청홍']
        )
        select_region = st.sidebar.selectbox(
            '지역을 선택하세요',
            ['춘천', '수원', '청주', '나주', '진주']
        )

    # 연도 선택 (2004~2024)
    select_year = st.sidebar.slider('연도를 선택하세요', 2004, 2024, 2024)

    # 사용 모델 선택
    if select_species == '배🍐':
        select_models = st.multiselect(
            '사용할 모델을 선택하세요',
            ['DVR', 'mDVR', 'CD']  # 배에 해당하는 모델들
        )
    elif select_species == '복숭아🍑':
        select_models = st.multiselect(
            '사용할 모델을 선택하세요',
            ['DVR', 'CD', 'NCD']  # 복숭아에 해당하는 모델들
        )

    # 예측 데이터 로드 (전체 연도를 포함)
    data_list = load_model_data(select_models, select_region, select_species)

    # 관측 데이터 로드
    observed_data_path = rf"C:\code\SAP_2024\02_Model\input\observe_data\flowering_date_{select_region}.csv"
    if os.path.exists(observed_data_path):
        observed_data = pd.read_csv(observed_data_path)
    else:
        observed_data = None

    # 개화일 변화 그래프 그리기 (전체 연도)
    if data_list:
        draw_bloom_date_graph(data_list, observed_data, select_region)


if __name__ == '__main__':
    main()
