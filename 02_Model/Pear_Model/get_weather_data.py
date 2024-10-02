import pandas as pd

def main():
    obsr_info = pd.read_csv('../input/종관기상_관측지점.csv')
    needed_code = [137, 281, 203, 232]
    filtered_obsr_info = obsr_info[obsr_info['지점코드'].isin(needed_code)]

    for code, region in zip(filtered_obsr_info['지점코드'], filtered_obsr_info['지점명']):
        print(code)
        url = f'https://api.taegon.kr/stations/{code}/?sy=2004&ey=2024&format=csv'
        df = pd.read_csv(url, skipinitialspace=True)
        print(df)
        df.to_csv(f'../output/{code}_{region}.csv', index=False, encoding='utf-8-sig')
if __name__ == '__main__':
    main()