import numpy as np
import pandas as pd
import os


def DVR_Model(df, C, D):
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    # 연도별로 데이터를 그룹화
    grouped_df = df.groupby('year')

    # 결과 저장을 위한 리스트
    bloom_results = []

    # 연도별로 데이터 처리
    for year, year_df in grouped_df:
        year_df = year_df[year_df['date'] >= pd.to_datetime(f'{year}-01-30')].copy()

        # 5°C 이상인 일평균 온도만 사용
        year_df['valid_temp'] = year_df['tavg'].apply(lambda T: T if T >= 5 else 0)

        # DVR 계산 (DVRT = C * exp(D * Tmean))
        year_df['DVR'] = year_df['valid_temp'].apply(lambda T: C * np.exp(D * T) if T > 0 else 0)

        # DVR 누적 계산 (개화 날짜는 DVR 누적값이 1 이상일 때)
        year_df['cumulative_DVR'] = year_df['DVR'].cumsum()

        # 개화 날짜 계산 (누적 DVR이 1 이상이 되는 첫 날짜)
        bloom_date = year_df.loc[year_df['cumulative_DVR'] >= 1, 'date'].min()
        bloom_results.append(bloom_date)

    # 결과 데이터프레임 만들기
    bloom_results_df = pd.DataFrame(bloom_results, columns=['full_bloom_date'])

    # 첫 번째 행을 드랍
    # bloom_results_df = bloom_results_df.drop(bloom_results_df.index[0])

    return bloom_results_df


# Tn : 최저온도, Tm : 평균온도, Tx : 최고온도, Tm: 평균온도, Tc : 임계온도
def chill_CD(tmin, tmax, Tc, tavg):


    if 0 <= Tc <= tmin <= tmax:
        return 0
    elif 0 <= tmin <= Tc <= tmax:
        return -((tavg - tmin) - ((tmax - Tc)**2) / (2 * (tmax - tmin)))
    elif 0 <= tmin <= tmax <= Tc:
        return (-(tavg - tmin))
    elif tmin <= 0 <= tmax <= Tc:
        return -((tmax**2) / (2 * (tmax - tmin)))
    elif tmin <= 0 <= Tc <= tmax:
        return -(tmax**2) / (2*(tmax-tmin)) - (((tmax - Tc)**2)/(2*(tmax-tmin)))

def anti_chill_CD(tmin, tmax, Tc, tavg):

    if 0 <= Tc <= tmin <= tmax:
        return (tavg - Tc)
    elif 0 <= tmin <= Tc <= tmax:
        return (tmax - Tc)**2/(2*(tmax - tmin))
    elif 0 <= tmin <= tmax <= Tc:
        return 0
    elif tmin <= 0 <= tmax <= Tc:
        return 0
    elif tmin <= 0 <= Tc <= tmax:
        return (tmax - Tc)**2/(2*(tmax - tmin))

def chill_NCD(tmin, tmax, Tc, tavg):

    if 0 <= Tc <= tmin <= tmax:
        return 0
    elif 0 <= tmin <= Tc <= tmax:
        return (tmin - Tc)**2 / (2 * (tmin - tmax))
    elif 0 <= tmin <= tmax <= Tc:
        return tavg-Tc
    elif tmin <= 0 <= tmax <= Tc:
        return (tavg - Tc) - (tmin**2 / (2 * (tmin - tmax)))
    elif tmin <= 0 <= Tc <= tmax:
        return (tmin - Tc)**2 / (2 * (tmin - tmax)) - (tmin**2 / (2 * (tmin - tmax)))
def anti_chill_NCD(tmin, tmax, Tc, tavg):


    if 0 <= Tc <= tmin <= tmax:
        return tavg - Tc
    elif 0 <= tmin <= Tc <= tmax:
        return (tmax - Tc)**2 / (2 * (tmax - tmin))
    elif 0 <= tmin <= tmax <= Tc:
        return 0
    elif tmin <= 0 <= tmax <= Tc:
        return 0
    elif tmin <= 0 <= Tc <= tmax:
        return (tmax - Tc)**2 / (2 * (tmax - tmin))



def CD_Model(df, Tc=5, Cr=-110, Hr=245):
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # 연도별로 데이터를 그룹화
    grouped_df = df.groupby('year')

    # 결과 저장을 위한 리스트
    bloom_results = []

    # 연도별로 데이터 처리
    for year, year_df in grouped_df:
        year_df = year_df[year_df['date'] >= pd.to_datetime(f'{year}-02-15')].copy()

        # Cd 계산
        year_df['Cd'] = year_df.apply(lambda row: chill_CD(row['tmin'], row['tmax'], Tc, row['tavg']), axis=1)
        year_df['Cd_cumsum'] = year_df['Cd'].cumsum()
    
        # Cr(추위 요구량)을 만족하는 시점 찾기 -> 휴면기 끝남
        year_df['Cr_reached'] = year_df['Cd_cumsum'] >= Cr
    
        # Cr이 충족된 시점 이후에 Ca 계산
        if year_df['Cr_reached'].any():
            # 첫 번째로 Cr을 충족한 날짜 찾기 -> 휴면기가 끝난
            rest_break_date = year_df.loc[year_df['Cr_reached']].index[0]
    
            # 해당 날짜 이후부터 Ca 계산
            year_df.loc[rest_break_date:, 'Ca'] = year_df.loc[rest_break_date:].apply(
                lambda row: anti_chill_CD(row['tmin'], row['tmax'], Tc, row['tavg']), axis=1)
            year_df['Ca_cumsum'] = year_df['Ca'].cumsum()
    
            # Hr(난방 요구량)이 충족되는 날짜 찾기
            year_df['Hr_reached'] = year_df['Ca_cumsum'] >= Hr
            if year_df['Hr_reached'].any():
                full_bloom_date = year_df.loc[year_df['Hr_reached']].iloc[0]
                # print(f"Full bloom predicted on: {full_bloom_date}")
                bloom_results.append(full_bloom_date)
            else:
                print("Hr(난방 요구량)에 도달하지 않았습니다.")
        else:
            print("Cr(추위 요구량)에 도달하지 않았습니다.")

    bloom_results_df = pd.DataFrame(bloom_results)
    bloom_results_df = bloom_results_df[['date']]
    bloom_results_df = bloom_results_df.rename(columns={'date': 'full_bloom_date'})
    return bloom_results_df



def NCD_Model(df, Tc=5, Cr=-110, Hr=245):
    
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # 연도별로 데이터를 그룹화
    grouped_df = df.groupby('year')

    # 결과 저장을 위한 리스트
    bloom_results = []

    # 연도별로 데이터 처리
    for year, year_df in grouped_df:
        year_df = year_df[year_df['date'] >= pd.to_datetime(f'{year}-02-15')].copy()

    
        # Cd 계산
        year_df['Cd'] = year_df.apply(lambda row: chill_NCD(row['tmin'], row['tmax'], Tc, row['tavg']), axis=1)
        year_df['Cd_cumsum'] = year_df['Cd'].cumsum()
    
        # Cr(추위 요구량)을 만족하는 시점 찾기 -> 휴면기 끝남
        year_df['Cr_reached'] = year_df['Cd_cumsum'] >= Cr
    
        # Cr이 충족된 시점 이후에 Ca 계산
        if year_df['Cr_reached'].any():
            # 첫 번째로 Cr을 충족한 날짜 찾기 -> 휴면기가 끝난
            rest_break_date = year_df.loc[year_df['Cr_reached']].index[0]
    
            # 해당 날짜 이후부터 Ca 계산
            year_df.loc[rest_break_date:, 'Ca'] = year_df.loc[rest_break_date:].apply(
                lambda row: anti_chill_NCD(row['tmin'], row['tmax'], Tc, row['tavg']), axis=1)
            year_df['Ca_cumsum'] = year_df['Ca'].cumsum()
    
            # Hr(난방 요구량)이 충족되는 날짜 찾기
            year_df['Hr_reached'] = year_df['Ca_cumsum'] >= Hr
            if year_df['Hr_reached'].any():
                full_bloom_date = year_df.loc[year_df['Hr_reached']].iloc[0]
                # print(f"Full bloom predicted on: {full_bloom_date}")
                bloom_results.append(full_bloom_date)
            else:
                print("Hr(난방 요구량)에 도달하지 않았습니다.")
        else:
            print("Cr(추위 요구량)에 도달하지 않았습니다.")

    bloom_results_df = pd.DataFrame(bloom_results)
    bloom_results_df = bloom_results_df[['date']]
    bloom_results_df = bloom_results_df.rename(columns={'date': 'full_bloom_date'})

    return bloom_results_df


def main():

    parameters = {
        '101': {# 춘천
            'chh': {'Tc': 5.0, 'Cr': -100, 'Hr': 244.0, 'C': 0.014, 'D': 0.062},
            'ymn': {'Tc': 5.0, 'Cr': -110, 'Hr': 245.0, 'C': 0.010, 'D': 0.093}
        },
        '119': { # 수원
            'cbj': {'Tc': 5.0, 'Cr': -107, 'Hr': 232.9, 'C': 0.008, 'D': 0.127},
            'chh': {'Tc': 5.0, 'Cr': -107, 'Hr': 240.1, 'C': 0.004, 'D': 0.194},
            'ymn': {'Tc': 6.0, 'Cr': -73, 'Hr': 180.2, 'C': 0.007, 'D': 0.138}
        },
        '232': {# 청원..천안
            'chh': {'Tc': 5.0, 'Cr': -133, 'Hr': 261.8, 'C': 0.011, 'D': 0.077},
            'ymn': {'Tc': 7.0, 'Cr': -95, 'Hr': 199.2, 'C': 0.002, 'D': 0.261}
        },
        '813': { # 청도
            'cjo': {'Tc': 9.0, 'Cr': -73, 'Hr': 137.2, 'C': 0.010, 'D': 0.077},
            'jhw': {'Tc': 9.0, 'Cr': -73, 'Hr': 134.0, 'C': 0.012, 'D': 0.065},
            'ymn': {'Tc': 5.2, 'Cr': -130, 'Hr': 277.4, 'C': 0.006, 'D': 0.129}
        },
        '710': { # 나주
            'chh': {'Tc': 8.0, 'Cr': -71, 'Hr': 149.6, 'C': 0.016, 'D': 0.053},
            'ymn': {'Tc': 8.0, 'Cr': -74, 'Hr': 150.0, 'C': 0.017, 'D': 0.043}
        },
        '192': { # 진주
            'chh': {'Tc': 6.0, 'Cr': -123, 'Hr': 215.7, 'C': 0.022, 'D': 0.029},
            'ymn': {'Tc': 5.1, 'Cr': -148, 'Hr': 271.0, 'C': 0.020, 'D': 0.028}
        }
    }

    folder_path = '../input/weather_data'

    # 파일 리스트를 가져오기
    files = os.listdir(folder_path)

    # 동일한 숫자로 시작하는 파일들 처리
    used_prefixes = set()  # 이미 처리한 파일의 숫자(prefix)를 기록할 집합

    for file in files:
        if file.endswith('.csv'):  # CSV 파일만 처리
            # 파일명에서 앞의 숫자 추출 (예: '101_춘천.csv' -> '101')
            prefix = file.split('_')[0]
            filename = file.split('_')[1].split('.')[0]
            # print(filename)


            # 동일한 prefix(숫자)로 시작하는 파일들만 처리
            if prefix not in used_prefixes:
                used_prefixes.add(prefix)  # 처리된 prefix 기록

                # 해당 파일에 대해 파라미터 적용
                if prefix in parameters:
                    # 필요한 파라미터 가져오기
                    param_set = parameters[prefix]

                    # 폴더 경로에 있는 파일을 불러오기
                    file_path = os.path.join(folder_path, file)
                    df = pd.read_csv(file_path)

                    # 품종별로 함수를 적용하는 예시
                    for cultivar, params in param_set.items():
                        Tc = params['Tc']
                        Cr = params['Cr']
                        Hr = params['Hr']
                        C = params['C']
                        D = params['D']

                        # 모델 실행
                        DVR_Model(df, C, D).to_csv(f'./Peach_Model_Output/{filename}_{cultivar}_DVR.csv')
                        CD_Model(df, Tc, Cr, Hr).to_csv(f'./Peach_Model_Output/{filename}_{cultivar}_CD.csv')
                        NCD_Model(df, Tc, Cr, Hr).to_csv(f'./Peach_Model_Output/{filename}_{cultivar}_NCD.csv')
                        print(f"Modeling for {filename}_{cultivar} is done!")


if __name__ == '__main__':
    main()