import pandas as pd
from urllib.parse import urlparse


# 블랙리스트
shortened_urls_df = pd.read_csv('features/filtered_short_urls.csv')


def is_shortened(url):
    matching_row = shortened_urls_df[shortened_urls_df['url'] == url]

    if not matching_row.empty:
        # 해당 URL이 존재하면, 라벨을 확인
        label = matching_row['label'].values[0]
        if label == 'good':
            return -1  # 정상 사이트
        elif label == 'bad':
            return 1  # 피싱 사이트
    else:
        # 해당 URL이 존재하지 않으면, 피싱 사이트로 간주
        return 1

# example_url = 'https://buly.kr/610SIJC'
# print(is_shortened(example_url))  # 정상 사이트인지 피싱 사이트인지 출력