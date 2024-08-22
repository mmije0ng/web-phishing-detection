from features import short_url_features
from features import url_based_feature
from features import content_based_features
from features import domainver1

import pandas as pd
import pickle
import time
import numpy as np

# 피처 이름 목록을 모델 학습 데이터의 피처 순서와 일치시킴
feature_order = [
    'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service', 'having_At_Symbol', 'double_slash_redirecting',
    'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length', 'Favicon',
    'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
    'Abnormal_URL', 'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain', 'DNSRecord',
    'web_traffic', 'Page_Rank', 'Google_Index', 'Links_pointing_to_page', 'Statistical_report'
]

def evaluate_url(url):
    # URL이 단축된 경우 복원
    url, is_shortened = short_url_features.check_url(url)
    print(f'단축 URL 여부: {is_shortened}')

    # 컨텐츠 기판 피처용 URLData 객체 생성
    response = content_based_features.get_request_url(url)
    
    # 피처를 딕셔너리로 정의
    features = {
        'URLURL_Length': url_based_feature.check_url_length(url),
        'port': url_based_feature.scan_non_standard_ports(url),
        'having_At_Symbol': url_based_feature.check_at_symbol(url),
        'double_slash_redirecting': url_based_feature.check_double_slash_redirecting(url),
        'Prefix_Suffix': url_based_feature.check_prefix_suffix(url),
        'Abnormal_URL': url_based_feature.check_abnormal_url(url),
        
        'RightClick': content_based_features.use_right_click(response),
        'popUpWidnow': content_based_features.popup_window_text(response),
        'Iframe': content_based_features.iFrame_redirection(response),
        'having_IPhaving_IP_Address': content_based_features.using_ip(url),
        'Favicon': content_based_features.check_favicon(url, response),
        'Request_URL': content_based_features.check_request_url(url, response),
        'URL_of_Anchor': content_based_features.check_url_of_anchor(url, response),
        'Links_in_tags': content_based_features.has_meta_tags(response),
        'SFH': content_based_features.check_sfh(url, response),
        'Submitting_to_email': content_based_features.check_submit_email(url, response),
        'Redirect': content_based_features.check_redirect_count(response),
        'on_mouseover': content_based_features.check_onmouseover_change(response),

        'Google_Index': domainver1.google_index(url),
        'Domain_registeration_length': domainver1.domain_registration_period(url),
        'age_of_domain': domainver1.domain_age(url),
        'DNSRecord': domainver1.dns_record(url),
        'SSLfinal_State': domainver1.ssl_certificate_status(url),
        'having_Sub_Domain': domainver1.having_subdomain(url),
        'HTTPS_token': domainver1.https_token(url),
        'web_traffic': domainver1.web_traffic(url),
        'Page_Rank': 0,
        'Links_pointing_to_page': 0,
        'Statistical_report': 0,

        'Shortining_Service': is_shortened,
    }

    # 피처 값을 올바른 순서로 정렬하여 단순 배열로 변환
    feature_values = [features[feature] for feature in feature_order]
    features_array = np.array(feature_values).reshape(1, -1)  # 2D 배열로 변환

    # 학습된 모델 로드 및 예측 수행
    # 다층퍼셉트론 모델 로드
    with open('model/mlp_model.pkl', 'rb') as f:
        mlp_model = pickle.load(f)

    # XGBoost 모델 로드
    with open('model/XGBoost_model.pkl', 'rb') as f:
        xgboost_model = pickle.load(f)
    
    # MLP 모델 예측
    mlp_prediction = mlp_model.predict(features_array)[0]
    mlp_probability = mlp_model.predict_proba(features_array)[0]
    mlp_phishing_prob = round(mlp_probability[1] * 100, 4)  # 피싱일 확률을 퍼센트로 변환하고 소수점 네 자리로 반올림

    # XGBoost 모델 예측
    xgboost_prediction = xgboost_model.predict(features_array)[0]
    xgboost_probability = xgboost_model.predict_proba(features_array)[0]
    xgboost_phishing_prob = round(xgboost_probability[1] * 100, 4)  # 피싱일 확률을 퍼센트로 변환하고 소수점 네 자리로 반올림

    # 피싱 여부 및 상세 설명
    phishing_mlp = mlp_prediction == 1
    phishing_xgboost = xgboost_prediction == 1
    explanation = []

    for feature_name, feature_value in features.items():
        if feature_name != 'Google_Index' and (feature_value == 1 or feature_value == 0):
            explanation.append(f"{feature_name}: {feature_value}")
    
    return {
        "url": (url),
        "mlp": (phishing_mlp, mlp_phishing_prob, explanation),
        "XGBoost": (phishing_xgboost, xgboost_phishing_prob, explanation)
    }

# 예시 URL
# 테스트용 URL 목록
# test_urls = [
#     # 단축 URL (정상 5개, 악성 5개)
#     'https://bit.ly/3xyz123',  # 정상, 복원 x, mlp: 0%, XGBoost: 0.0165%
#     'https://tinyurl.com/y6abcd',  # 정상, 복원 x, mlp: 0%, XGBoost: 0.0165%
#     'https://goo.gl/abc123',  # 정상, 복원 x, mlp: 0%, XGBoost: 0.0138%
#     'https://ow.ly/abcd1234',  # 정상, 복원 o, mlp: 8.4119%, XGBoost: 99.9725%
#     'https://bit.ly/4abcd',  # 정상, 복원 o, mlp: 0%, XGBoost: 0.0006%
#     'https://bit.ly/malicious1',  # 악성, 복원 x, mlp: 0%, XGBoost: 0.0165%
#     'https://cli.gs/malware',  # 악성, 복원 x, mlp: 98.9646%, XGBoost: 99.9985%
#     'https://v.gd/phishing',  # 악성, 0% 복원 x, mlp: 0%, XGBoost: 0.0165%
#     'https://bc.vc/fraud',  # 악성, 0%, 복원 o, mlp: 0%, XGBoost: 0.0165%
#     'https://po.st/scam',  # 악성, 0%, 복원 x, mlp: 0%, XGBoost: 0.0009%

#     # 일반 URL (정상 5개, 악성 5개)
#     'https://www.google.com',  # 정상, mlp: 0%, XGBoost: 0.0070%
#     'https://www.wikipedia.org',  # 정상, mlp: 0%, XGBoost: 0%
#     'https://www.python.org',  # 정상, mlp: 0%, XGBoost: 0.0063%
#     'https://www.github.com',  # 정상, mlp: 0%, XGBoost: 0.0056%
#     'https://www.stackoverflow.com',  # 정상, mlp: 0%, XGBoost: 0.0025%
#     'http://malicious-site.com',  # 악성, mlp: 20.1776%, XGBoost: 99.9938%
#     'http://phishing-site.com',  # 악성, mlp: 100%, XGBoost: 99.9999%
#     'http://fraud-site.org',  # 악성, mlp: 99.9929%, XGBoost: 99.9987%
#     'http://fake-login.net',  # 악성, mlp: 99.9929%, XGBoost: 99.9987%
#     'http://dangerous-site.biz',  # 악성, mlp: 99.9929%, XGBoost: 99.9987%

# ]

test_urls = [
    # 피싱 5개
    'https://buly.kr/BITBije', # 복원 o, mlp: 0%, XGBoost: 0.0120%
    'https://buly.kr/9BU5wxI', # 복원 o, mlp: 0.0001%, XGBoost: 0.4235%
    'https://buly.kr/Gkqg82e', # 복원 o, mlp: 0.0000%, XGBoost: 66.0719%
    'https://buly.kr/GZvv9En', # 복원 o, mlp: 0.0000%, XGBoost: 0.0043%
    'https://buly.kr/jXirow', # 복원 o, mlp: 0.0000%, XGBoost: 0.0005%

    # 일반 5개
    'https://buly.kr/610SIJC', # 복원 o, mlp: 0.0000%, XGBoost: 0.0001%
    'https://buly.kr/2qWodcD', # 복원 o, mlp: 0.0000%, XGBoost: 0.0002%
    'https://buly.kr/C08De2i', # 복원 o, mlp: 0.0000%, XGBoost: 0.0870%
    'https://url.kr/b2ecua', # 복원 o, mlp: 0.0000%, XGBoost: 0.1792%
    'https://tinyurl.com/3z5h4h3w' # 복원 o, mlp: 0.0000%, XGBoost: 0.0002%
]

# test_urls = [
#     'http://html.house/l7ceeid6.html' # 일반 URL, 피싱
# ]

# 각 URL에 대해 평가 수행
for url in test_urls:
    start_time = time.time()
    results = evaluate_url(url)
    end_time = time.time()

    # MLP 결과 출력
    mlp_phishing, mlp_probability, mlp_explanations = results["mlp"]
    print(f"MLP 다층퍼셉트론 모델 결과:")
    print(f"URL: {results['url']}")
    print(f"피싱 확률: {mlp_probability:.4f}%")
    print(f"피싱 여부: {'Yes' if mlp_phishing else 'No'}")
    if mlp_explanations:
        print("의심 피처들:")
        for explanation in mlp_explanations:
            print(f" - {explanation}")
    print("-" * 25)

    # XGBoost 결과 출력
    xgboost_phishing, xgboost_probability, xgboost_explanations = results["XGBoost"]
    print(f"XGBoost 모델 결과:")
    print(f"URL: {results['url']}")
    print(f"피싱 확률: {xgboost_probability:.4f}%")
    print(f"피싱 여부: {'Yes' if xgboost_phishing else 'No'}")
    if xgboost_explanations:
        print("의심 피처들:")
        for explanation in xgboost_explanations:
            print(f" - {explanation}")
    print("-" * 50)

    print(f"분석 시간: {end_time - start_time:.2f} seconds")
    print("=" * 50)