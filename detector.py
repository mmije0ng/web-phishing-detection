from features import short_url_features
from features import url_based_feature
from features import content_based_features
from features import domainver1

import pandas as pd
import pickle
import time
import numpy as np

def evaluate_url(url):
    # URL이 단축된 경우 복원
    url, is_shortened = short_url_features.check_url(url)
    print(f'단축 URL 여부: {is_shortened}')

    # 피처를 딕셔너리로 정의
    features = {
        'URLURL_Length': url_based_feature.check_url_length(url),
        'port': url_based_feature.scan_non_standard_ports(url),
        'having_At_Symbol': url_based_feature.check_at_symbol(url),
        'double_slash_redirecting': url_based_feature.check_double_slash_redirecting(url),
        'Prefix_Suffix': url_based_feature.check_prefix_suffix(url),
        'Abnormal_URL': url_based_feature.check_abnormal_url(url),
        
        'RightClick': content_based_features.use_right_click(url),
        'popUpWidnow': content_based_features.popup_window_text(url),
        'Iframe': content_based_features.iFrame_redirection(url),
        'having_IPhaving_IP_Address': content_based_features.using_ip(url),
        'Favicon': content_based_features.check_favicon(url),
        'Request_URL': content_based_features.check_request_url(url),
        'URL_of_Anchor': content_based_features.check_url_of_anchor(url),
        'Links_in_tags': content_based_features.has_meta_tags(url),
        'SFH': content_based_features.check_sfh(url),
        'Submitting_to_email': content_based_features.check_submit_email(url),
        'Redirect': content_based_features.check_redirect_count(url),
        'on_mouseover': content_based_features.check_onmouseover_change(url),

        'Google_Index': domainver1.google_index(url),
        'Domain_registeration_length': domainver1.domain_registration_period(url),
        'age_of_domain': domainver1.domain_age(url),
        'DNSRecord': domainver1.dns_record(url),
        'SSLfinal_State': domainver1.ssl_certificate_status(url),
        'having_Sub_Domain': domainver1.having_sub_domain(url),
        'HTTPS_token': domainver1.https_token(url),
        'web_traffic': domainver1.web_traffic(url),
        'Page_Rank': domainver1.page_rank(url),
        'Links_pointing_to_page': domainver1.links_pointing_to_page(url),
        'Statistical_report': domainver1.statistical_report(url),

        'Shortining_Service': is_shortened,
    }

    # 피처 이름 목록을 모델 학습 데이터의 피처 순서와 일치시킴
    feature_order = [
        'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service', 'having_At_Symbol', 'double_slash_redirecting',
        'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length', 'Favicon',
        'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
        'Abnormal_URL', 'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain', 'DNSRecord',
        'web_traffic', 'Page_Rank', 'Google_Index', 'Links_pointing_to_page', 'Statistical_report'
    ]

    # 피처 값을 올바른 순서로 정렬하여 단순 배열로 변환
    feature_values = [features[feature] for feature in feature_order]
    features_array = np.array(feature_values).reshape(1, -1)  # 2D 배열로 변환

    # 학습된 모델 로드
    with open('model/mlp_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    # 피처 배열을 사용하여 예측 수행
    prediction = model.predict(features_array)[0]
    probability = model.predict_proba(features_array)[0]

    # 피싱 확률 계산
    phishing_prob = round(probability[1] * 100, 4)  # 피싱일 확률을 퍼센트로 변환하고 소수점 네 자리로 반올림

    # 피싱 여부 및 상세 설명
    phishing = prediction == 1
    explanation = []

    for feature_name, feature_value in features.items():
        if feature_value == 1 or feature_value == 0:
            explanation.append(f"{feature_name}: {feature_value}")
    
    return phishing, phishing_prob, explanation

# 예시 URL
# 테스트용 URL 목록
test_urls = [
    # 단축 URL (정상 5개, 악성 5개)
    'https://bit.ly/3xyz123',  # 정상
    'https://tinyurl.com/y6abcd',  # 정상
    'https://goo.gl/abc123',  # 정상, 0.29%
    'https://ow.ly/abcd1234',  # 정상
    'https://bit.ly/4abcd',  # 정상
    'https://bit.ly/malicious1',  # 악성
    'https://cli.gs/malware',  # 악성
    'https://v.gd/phishing',  # 악성
    'https://bc.vc/fraud',  # 악성
    'https://po.st/scam',  # 악성

    # 일반 URL (정상 5개, 악성 5개)
    'https://www.google.com',  # 정상
    'https://www.wikipedia.org',  # 정상
    'https://www.python.org',  # 정상
    'https://www.github.com',  # 정상
    'https://www.stackoverflow.com',  # 정상
    'http://malicious-site.com',  # 악성
    'http://phishing-site.com',  # 악성
    'http://fraud-site.org',  # 악성
    'http://fake-login.net',  # 악성
    'http://dangerous-site.biz',  # 악성
]

# 각 URL에 대해 평가 수행
for url in test_urls:
    start_time = time.time()
    phishing, probability, explanations = evaluate_url(url)
    end_time = time.time()

    print(f"URL: {url}")
    print(f"피싱 확률: {probability:.2f}%")
    print(f"피싱 여부: {'Yes' if phishing else 'No'}")
    if explanations:
        print("의심 피처들:")
        for explanation in explanations:
            print(f" - {explanation}")

    print(f"분석 시간: {end_time - start_time:.2f} seconds")
    print("-" * 50)