import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 불러오기
df = pd.read_csv("telecom_customer_churn.csv")
print(df.head())

# 필요한 특징 선택
features = [
    'Age', 'Number of Dependents', 'Latitude', 'Longitude',
    'Number of Referrals', 'Tenure in Months', 'Avg Monthly Long Distance Charges',
    'Avg Monthly GB Download', 'Monthly Charge', 'Total Charges', 'Total Refunds',
    'Total Extra Data Charges', 'Total Long Distance Charges', 'Total Revenue'
]
df_selected = df[features]

# 상관 계수 계산
correlation_matrix = df_selected.corr()

# 히트맵 그리기
plt.figure(figsize=(15, 12))
heatmap = sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)

# x축과 y축의 글씨 기울이기
heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=50, horizontalalignment='right')
heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0, horizontalalignment='right')

plt.title('Correlation Heatmap')
plt.tight_layout

output_path = './heatmap_final.png'
plt.savefig(output_path, format='png')

plt.show()