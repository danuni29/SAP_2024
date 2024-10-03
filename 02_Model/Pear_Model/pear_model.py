import pandas as pd
import numpy as np
import math
import os

def valid_month(df):

    # 전년도 10월 ~ 2월까지
    # 전년도 10, 11, 12월을 그 다음연도로 표현 => agri_year
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    df['agri_year'] = df['year']

    df.loc[df['month'].isin([10, 11, 12]), 'agri_year'] = df['year'] + 1

    # 2003년 1월과 2월 데이터 삭제
    df = df[~((df['year'] == 2003) & (df['month'].isin([1, 2])))]

    # 불필요한 데이터 제거
    df = df[~df['month'].isin([7, 8, 9])]

    # df.to_csv(('./test.csv'))

    return df

def DVR_model(df):
    # parameter
    # temp_data : 일평균 기온
    # A = 107.94
    # B = 0.9

    # 예상만개일 : DVR이 100에 도달하는 순간
    # 전년도 10월 1일 ~ 2월 15일 ????

    # temp_data = df['tavg']

    A = 107.94
    B = 0.9
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    results = []

    # agri_year별로 그룹화하여 반복
    for year, group in df.groupby('year'):
        DVS = 0
        # print(year, group)


        for tavg, date in group[['tavg', 'date']].itertuples(index=False):


            if tavg > 5:
                DVR = (1 / (A * (B ** tavg))) * 100
                DVS += DVR
                # print(DVS, DVR)

                if DVS >= 100:
                    results.append({'DVS': DVS, 'full_bloom_date': date})
                    break


            # 결과를 DataFrame으로 변환하고 CSV 파일로 저장
    result_df = pd.DataFrame(results)
        # result_df.to_csv('./DVR_Model_result.csv', index=False)
    return result_df
#  ---------------------------------------------------
# mDVR Model

def DVR1(T):
    dvr1 = 0

    if T < -6:
        dvr1 = 0

    elif -6 <= T < 0:
        dvr1 = 1.333 * (10 ** (-3)) + 2.222 * (10 ** (-4)) * T

    elif 0 <= T < 6:
        dvr1 = 1.333 * (10 ** (-3))

    elif 6 <= T < 9:
        dvr1 = 2.276e-3 - 1.571e-4 * T
    elif 9 <= T <= 12:
        dvr1 = 3.448e-3 - 2.874e-4 * T

    elif T >= 12:
        dvr1 = 0

    return dvr1
def DVR2(T):

    dvr2 = 0

    if T <= 20:
        dvr2 = math.exp(35.27 - (12094 / (T + 273)))

    elif T >= 20:
        dvr2 = math.exp(5.82 - (3474 / (T + 273)))

    elif T < 0:
        dvr2 = 0

    return dvr2



# 시간별 DVR1 & DVR2 적용

def mDVR_model(df):
    # 날짜 정보 생성
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # 연도별로 데이터를 그룹화
    grouped_df = df.groupby('year')

    # 결과 저장을 위한 리스트
    bloom_results = []

    # 연도별로 데이터 처리
    for year, year_df in grouped_df:
        year_df = year_df[year_df['date'] >= pd.to_datetime(f'{year}-02-15')].copy()

        # 시간별 온도 및 DVR1, DVR2 계산
        for hour in range(0, 24):
            if 0 <= hour <= 3:
                year_df[f'temp_{hour}H'] = (year_df['tmax'].shift(1) - year_df['tmin']) * (
                            np.sin((4 - hour) * 3.14 / 30) ** 2) + year_df['tmin']
            elif 4 <= hour <= 13:
                year_df[f'temp_{hour}H'] = (year_df['tmax'] - year_df['tmin']) * (np.sin((hour - 4) * 3.14 / 18) ** 2) + \
                                           year_df['tmin']
            elif 14 <= hour <= 23:
                year_df[f'temp_{hour}H'] = (year_df['tmax'] - year_df['tmin'].shift(-1)) * (
                            np.sin((28 - hour) * 3.14 / 30) ** 2) + year_df['tmin'].shift(-1)

            year_df[f'DVR1_{hour}H'] = year_df[f'temp_{hour}H'].apply(DVR1)
            year_df[f'DVR2_{hour}H'] = year_df[f'temp_{hour}H'].apply(DVR2)

        # 2월 15일 이후 데이터만 사용
        end_of_endodormancy = pd.to_datetime('02-15', format='%m-%d')
        year_df = year_df[year_df['date'] >= end_of_endodormancy]

        # 2월 15일 DVR1 값을 1로 지정
        year_df.loc[year_df['date'] == pd.to_datetime(f'{year}-02-15'), 'DVR1_initial'] = 1

        # DVR1 누적 합계 계산 (2월 15일에 DVR1 값을 1로 지정하고 시작)
        dvr1_columns = [col for col in year_df.columns if 'DVR1_' in col]
        year_df['cumulative_DVR1'] = year_df[dvr1_columns].sum(axis=1).cumsum()
        year_df['cumulative_DVR1'] += year_df['DVR1_initial'].fillna(0)  # 2월 15일 값을 1로 시작하여 누적

        # DVR2는 DVR1이 2에 도달한 이후부터 누적
        year_df['cumulative_DVR2'] = 0  # 초기값 설정
        dvr2_columns = [col for col in year_df.columns if 'DVR2_' in col]
        start_accumulation = False

        for i in range(len(year_df)):
            if year_df.iloc[i]['cumulative_DVR1'] >= 2:
                start_accumulation = True
            if start_accumulation:
                year_df.iloc[i, year_df.columns.get_loc('cumulative_DVR2')] = year_df.iloc[i][dvr2_columns].sum()

        # DVR2 누적 합계 계산
        year_df['cumulative_DVR2'] = year_df['cumulative_DVR2'].cumsum()
        # 개화 시기 예측
        df_reach_bloom = year_df[year_df['cumulative_DVR2'] >= 0.9593]

        if not df_reach_bloom.empty:
            bloom_date = df_reach_bloom.iloc[0]['date']
            bloom_results.append({'year': year, 'predicted_bloom_date': bloom_date})
        else:
            bloom_results.append({'year': year, 'predicted_bloom_date': None})

    # 결과를 DataFrame으로 변환하여 반환
    bloom_results_df = pd.DataFrame(bloom_results)
    return bloom_results_df


    # 결과를 DataFrame으로 변환하여 반환
    # bloom_results_df = pd.DataFrame(bloom_results)
    # print(bloom_results_df)
    # return bloom_results_df


# chill_unit과 heat_unit을 계산하는 함수
def calculate_units(row):
    Tc = 5.4  # 기준 온도
    tmax = row['tmax']
    tmin = row['tmin']
    tavg = row['tavg']

    chill = 0
    anti_chill = 0

    if 0 <= Tc <= tmin <= tmax:
        chill = 0
        anti_chill = tavg - Tc
    elif 0 <= tmin <= Tc <= tmax:
        chill = -((tavg - tmin) - (tmax - Tc) / 2)
        anti_chill = (tmax - Tc) / 2
    elif 0 <= tmin <= tmax <= Tc:
        chill = -(tavg - tmin)
        anti_chill = 0
    elif tmin < 0 <= tmax <= Tc:
        chill = (tmax / (tmax - tmin)) * (tmax / 2)
        anti_chill = 0
    elif tmin < 0 < Tc < tmax:
        chill = -(((tmax / (tmax - tmin)) * (tmax / 2)) - ((tmax - Tc) / 2))
        anti_chill = (tmax - Tc) / 2

    return pd.Series([chill, anti_chill])


# main 함수
def calculate_chill_heat(df):
    Hr = 272  # 고온요구량
    Cr = -86.4  # 저온요구량

    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # 각 행에 대해 chill_unit과 heat_unit 계산
    df[['chill_unit', 'heat_unit']] = df.apply(calculate_units, axis=1)

    result_df = pd.DataFrame()
    grouped_df = df.groupby('year')


    # 연도별로 데이터 처리
    for year, year_df in grouped_df:
        # print(year, year_df)

        year_df['cumulative_heat'] = 0.0

        # 2월 15일 이후부터 가온량 계산
        year_df = year_df[year_df['date'] >= pd.to_datetime(f'{year}-02-15')].copy()

        # 누적 가온량 계산
        year_df['cumsum_heat_unit'] = year_df['heat_unit'].cumsum()

        # Cr 이상인 데이터만 사용
        year_df = year_df[year_df['cumsum_heat_unit'] >= Cr]

        # 만개예상일 계산
        year_date = year_df[year_df['cumsum_heat_unit'] >= Hr].head(1)

        result_df = pd.concat([result_df, year_date])

    cd_date = result_df[['year', 'date']].reset_index(drop=True)
    cd_date = cd_date.rename(columns={"date": "CD"})
    # cd_date.to_csv('CD_Model_result.csv', index=False)
    return cd_date


def main():

    input_dir = '../input/weather_data'
    output_dir = '../Pear_Model_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        if file_name.endswith('.csv'):  # CSV 파일만 처리
            base_file_name = os.path.splitext(file_name)[0]

            output_file_path = os.path.join(output_dir, file_name)

            df = pd.read_csv(file_path)
            DVR_model(df).to_csv(os.path.join(output_dir, f'DVR_Model_result_{base_file_name}.csv'), index=False)
            mDVR_model(df).to_csv(os.path.join(output_dir, f'mDVR_model_result_{base_file_name}.csv'), index=False)
            calculate_chill_heat(df).to_csv(os.path.join(output_dir, f'CD_Model_result_{base_file_name}.csv'), index=False)

            print(f"Processed file saved: {output_file_path}")



if __name__ == '__main__':
    main()
