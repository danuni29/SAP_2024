import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import numpy as np
import os

start_year = 2001
year_for = 22

def dvr_e(df, C, D):
    if df['tavg'] >= 5:
        return C * np.exp(D * df['tavg'])
    else:
        return 0

def ischill(df, Tc):
    Tn = df['tmin']
    Tx = df['tmax']
    Tm = (Tx + Tn)/2
    if 0 <= Tc <= Tn <= Tx:
        return 0
    elif 0 <= Tn <= Tc <= Tx:
        return -((Tm - Tn) - ((Tx - Tc)**2) / (2 * (Tx - Tn)))
    elif 0 <= Tn <= Tx <= Tc:
        return (-(Tm - Tn))
    elif Tn <= 0 <= Tx <= Tc:
        return -((Tx**2) / (2 * (Tx - Tn)))
    elif Tn <= 0 <= Tc <= Tx:
        return -(Tx**2)/ (2*(Tx-Tn)) - (((Tx - Tc)**2)/(2*(Tx-Tn)))


def isantichill(df, Tc):
    Tn = df['tmin']
    Tx = df['tmax']
    Tm = (Tx + Tn) / 2

    if 0 <= Tc <= Tn <= Tx:
        return (Tm - Tc)
    elif 0 <= Tn <= Tc <= Tx:
        return (Tx - Tc)**2/(2*(Tx - Tn))
    elif 0 <= Tn <= Tx <= Tc:
        return 0
    elif Tn <= 0 <= Tx <= Tc:
        return 0
    elif Tn <= 0 <= Tc <= Tx:
        return (Tx - Tc)**2/(2*(Tx - Tn))




def models(df, Tc, C, D):
    df = df[(df['date'].dt.month > 1) | ((df['date'].dt.month == 1) & (df['date'].dt.day >= 30))]
    df['Cdt'] = df.apply(lambda x: ischill(x, Tc[x['location']]), axis=1)
    df['Cat'] = df.apply(lambda x: isantichill(x, Tc[x['location']]), axis=1)
    df['Cd'] = abs(df['Cdt']).cumsum()
    df['Ca'] = abs(df['Cat']).cumsum()
    df['DVRi'] = df.apply(lambda x: dvr_e(x, C[x['location']], D[x['location']]), axis=1)
    df['DVR'] = df['DVRi'].cumsum()

    return df

def main():
    results = []
    ob = pd.read_csv('data/observe.csv')
    C = {'101': 0.011, '119': 0.007, '131': 0.002, '143': 0.006, '156': 0.017, '192': 0.020}
    D = {'101': 0.093, '119': 0.138, '131': 0.261, '143': 0.129, '156': 0.043, '192': 0.028}
    Tc = {'101': 5, '119': 6, '131': 7, '143': 5.2, '156': 8, '192': 5.1}
    Cr = {'101': -110, '119': -73, '131': -95, '143': -130, '156': -74, '192': -148}
    Hr = {'101': 245, '119': 180.2, '131': 199.2, '143': 277.4, '156': 150, '192': 271}

    df_loc = pd.read_csv('data/location.csv')
    for loc in tqdm(df_loc['loc_num']):
        url = f'https://api.taegon.kr/station/{loc}/?sy={start_year}&ey={start_year + year_for}&format=csv'
        response = requests.get(url)
        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_data), skipinitialspace=True)

        df = df[['year', 'month', 'day', 'tavg', 'tmax', 'tmin', 'rainfall', 'snow']]
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['location'] = str(loc)
        df['DOY'] = df['date'].dt.dayofyear
        for year in range(start_year, start_year + year_for + 1):
            year_df = df[df['year'] == year].copy()
            result = models(year_df, Tc, C, D)
            results.append(result)

    result_df = pd.concat(results, axis=0, ignore_index=False)
    output_dir_txt = "./output"

    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    result_df.to_csv(f'{output_dir_txt}/results.csv')

if __name__ == '__main__':
    main()