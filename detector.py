import asyncio
from features import short_url_features, url_based_feature, content_based_features, domain_based_features
import pickle
import numpy as np
import time

# 피처 이름 목록을 모델 학습 데이터의 피처 순서와 일치시킴
feature_order = [
    'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service', 'having_At_Symbol', 'double_slash_redirecting',
    'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State', 'Favicon',
    'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
    'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain', 'Google_Index'
]

async def evaluate_url(url):

    # URL이 단축된 경우 복원
    is_shortened = await asyncio.to_thread(short_url_features.is_shortened, url)
    print(f'단축 URL 여부: {is_shortened}')

    # 컨텐츠 기반 피처용 URLData 객체 생성
    response = await asyncio.to_thread(content_based_features.get_request_url, url)
    
    # 비동기 함수로 개별 피처들을 동시에 실행
    tasks = {
        'URLURL_Length': asyncio.to_thread(url_based_feature.check_url_length, url),
        'port': asyncio.to_thread(url_based_feature.scan_non_standard_ports, url),
        'having_At_Symbol': asyncio.to_thread(url_based_feature.check_at_symbol, url),
        'double_slash_redirecting': asyncio.to_thread(url_based_feature.check_double_slash_redirecting, url),
        'Prefix_Suffix': asyncio.to_thread(url_based_feature.check_prefix_suffix, url),
        
        'RightClick': asyncio.to_thread(content_based_features.use_right_click, response),
        'popUpWidnow': asyncio.to_thread(content_based_features.popup_window_text, response),
        'Iframe': asyncio.to_thread(content_based_features.iFrame_redirection, response),
        'having_IPhaving_IP_Address': asyncio.to_thread(content_based_features.using_ip, url),
        'Favicon': asyncio.to_thread(content_based_features.check_favicon, url, response),
        'Request_URL': asyncio.to_thread(content_based_features.check_request_url, url, response),
        'URL_of_Anchor': asyncio.to_thread(content_based_features.check_url_of_anchor, url, response),
        'Links_in_tags': asyncio.to_thread(content_based_features.has_meta_tags, response),
        'SFH': asyncio.to_thread(content_based_features.check_sfh, url, response),
        'Submitting_to_email': asyncio.to_thread(content_based_features.check_submit_email, url, response),
        'Redirect': asyncio.to_thread(content_based_features.check_redirect_count, response),
        'on_mouseover': asyncio.to_thread(content_based_features.check_onmouseover_change, response),

        'Google_Index': asyncio.to_thread(domain_based_features.google_index, url),
        'age_of_domain': asyncio.to_thread(domain_based_features.age_of_domain, url),
        'SSLfinal_State': asyncio.to_thread(domain_based_features.sslfinal_state, url),
        'having_Sub_Domain': asyncio.to_thread(domain_based_features.having_subdomain, url),
        'HTTPS_token': asyncio.to_thread(domain_based_features.https_token, url),

        'Shortining_Service': asyncio.to_thread(short_url_features.is_shortened, url)
    }

    # 모든 비동기 작업을 병렬로 실행
    feature_results = await asyncio.gather(*tasks.values())
    features = dict(zip(tasks.keys(), feature_results))

    # 피처 값을 올바른 순서로 정렬하여 단순 배열로 변환
    feature_values = [features[feature] for feature in feature_order]
    features_array = np.array(feature_values).reshape(1, -1)  # 2D 배열로 변환

    # 학습된 모델 로드 및 예측 수행

    # 다층퍼셉트론 모델 로드
    with open('model/mlp_column_drop_model.pkl', 'rb') as f:
        mlp_model = pickle.load(f)

    # XGBoost 모델 로드
    with open('model/XGBoost_column_drop_model.pkl', 'rb') as f:
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
        if feature_value == 1 or feature_value == 0:
            explanation.append(f"{feature_name}: {feature_value}")
    
    return {
        "url": url,
        "mlp": (phishing_mlp, mlp_phishing_prob, explanation),
        "XGBoost": (phishing_xgboost, xgboost_phishing_prob, explanation)
    }

# 테스트용 URL 목록
# test_urls = [
#     # 단축 URL (정상 5개, 악성 5개)
#     'https://bit.ly/3xyz123',  # 정상, 복원 x, mlp: 100.0000%, XGBoost: 59.4475%
#     'https://tinyurl.com/y6abcd',  # 정상, 복원 x, mlp: 100.0000%, XGBoost: 59.4475%
#     'https://goo.gl/abc123',  # 정상, 복원 x, mlp: 100.0000%, XGBoost: 59.4475%
#     'https://ow.ly/abcd1234',  # 정상, 복원 o, mlp: 100.0000%, XGBoost: 99.9788%
#     'https://bit.ly/4abcd',  # 정상, 복원 o, mlp: 0%, XGBoost: 1.5160%
#     'https://bit.ly/malicious1',  # 악성, 복원 x, mlp: 100.0000%, XGBoost: 59.4475%
#     'https://cli.gs/malware',  # 악성, 복원 x, mlp: 100.0000%, XGBoost: 99.9788%
#     'https://v.gd/phishing',  # 악성, 0% 복원 x, mlp: 100.0000%, XGBoost: 59.4475%
#     'https://bc.vc/fraud',  # 악성, 0%, 복원 o, mlp: 99.9994%, XGBoost: 94.4168%
#     'https://po.st/scam',  # 악성, 0%, 복원 x, mlp: 0.0000%, XGBoost: 1.3971%

#     # 일반 URL (정상 5개, 악성 5개)
#     'https://www.google.com',  # 정상, mlp: 0.0000%, XGBoost: 0.5252%
#     'https://www.wikipedia.org',  # 정상, mlp: 0.0003%, XGBoost: 0%
#     'https://www.python.org',  # 정상, mlp: 0.0000%, XGBoost: 1.5160%
#     'https://www.github.com',  # 정상, mlp: 8.8258%, XGBoost: 4.7550%
#     'https://www.stackoverflow.com',  # 정상, mlp: 0.0000%, XGBoost: 0.8729%
#     'http://malicious-site.com',  # 악성, mlp: 100.0000%, XGBoost: 99.9999%
#     'http://phishing-site.com',  # 악성, mlp:  100.0000%, XGBoost: 98.3522%
#     'http://fraud-site.org',  # 악성, mlp: 100.0000%, XGBoost: 88.3212%
#     'http://fake-login.net',  # 악성, mlp: 100.0000%, XGBoost: 88.3212%
#     'http://dangerous-site.biz',  # 악성, mlp: 100.0000%, XGBoost:88.3212%
# ]

# 테스트용 URL 목록
test_urls = [
    # 피싱 5개
    'https://buly.kr/BITBije', # 복원 o, mlp: 0.0000%, XGBoost: 1.0463%
    'https://buly.kr/9BU5wxI', # 복원 o, mlp: 0.0038%, XGBoost: 0.4673%
    'https://buly.kr/Gkqg82e', # 복원 o, mlp: 0.0000%, XGBoost: 0.1185%
    'https://buly.kr/GZvv9En', # 복원 o, mlp: 0.0000%, XGBoost: 1.7451%
    'https://buly.kr/jXirow', # 복원 o, mlp: 0.0000%, XGBoost: 0.0727%

    # 일반 5개
    'https://buly.kr/610SIJC', # 복원 o, mlp: 0.0000%, XGBoost: 0.0003%
    'https://buly.kr/2qWodcD', # 복원 o, mlp: 0.0000%, XGBoost: 0.0009%
    'https://buly.kr/C08De2i', # 복원 o, mlp: 0.0000%, XGBoost: 1.9202%
    'https://url.kr/b2ecua', # 복원 o, mlp: 0.0000%, XGBoost: 0.2273%
    'https://tinyurl.com/3z5h4h3w' # 복원 o, mlp: 0.0000%, XGBoost: 0.0011%
]

# 메인 함수에서 비동기 함수 실행
async def main():
    for url in test_urls:
        start_time = time.time()
        results = await evaluate_url(url)
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

        # 실행 시간 출력
        elapsed_time = end_time - start_time
        print(f"실행 시간: {elapsed_time:.4f}초\n")

# 비동기 실행
asyncio.run(main())