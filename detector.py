from features import short_url_features
from features import url_based_feature
from features import content_based_features
from features import domainver1

import pandas as pd
import pickle
import time

def evaluate_url(url):
    # URL이 단축된 경우 복원
    url, is_shortened = short_url_features.check_url(url)
    print(f'단축 URL 여부: {is_shortened}')

    # 피처를 딕셔너리로 정의
    features = {
        'URL Length': url_based_feature.check_url_length(url),
        'Port Scan': url_based_feature.port_scan(url),
        'Having At Symbol': url_based_feature.check_at_symbol(url),
        'Double Slash Redirecting': url_based_feature.check_double_slash_redirecting(url),
        'Prefix/Suffix': url_based_feature.check_double_slash_redirecting(url),
        'Abnormal URL': url_based_feature.check_abnormal_url(url),
        
        'Right Click Disabled': content_based_features.use_right_click(url),
        'Popup Window Contains Text Field': content_based_features.popup_window_text(url),
        'iFrame Redirection': content_based_features.iFrame_redirection(url),
        'Using IP': content_based_features.using_ip(url),
        'Favicon': content_based_features.check_favicon(url),
        'Request URL': content_based_features.check_request_url(url),
        'URL of Anchor': content_based_features.check_url_of_anchor(url),
        'Links in Meta, Script, and Link tags': content_based_features.has_meta_tags(url),
        'SFH (Server Form Handler)': content_based_features.check_sfh(url),
        'Submit Email': content_based_features.check_submit_email(url),
        'Redirect Count': content_based_features.check_redirect_count(url),
        'OnMouseOver Changes Status': content_based_features.check_onmouseover_change(url),

        'Google Index': domainver1.google_index(url),
        'Domain Registration Length': domainver1.domain_registration_period(url),
        'Age Of Domain': domainver1.domain_age(url),
        'DNS Record': domainver1.dns_record(url),
        'SSLfinal State': domainver1.ssl_certificate_status(url),
        'Having Sub Domain': domainver1.having_sub_domain(url),
        'HTTPS Token': domainver1.https_token(url),
        'Web Traffic': domainver1.web_traffic(url),
        'Page Rank': domainver1.page_rank(url),
        'Links Pointing to Page': domainver1.links_pointing_to_page(url),
        'Statistical Report': domainver1.statistical_report(url),

        'Shortening Service': is_shortened
    }

    # 피처 이름 목록을 모델 학습 데이터의 피처 순서와 일치시킴
    feature_order = [
        'URL Length', 'Port Scan', 'Having At Symbol', 'Double Slash Redirecting', 'Prefix/Suffix', 'Abnormal URL',
        'Right Click Disabled', 'Popup Window Contains Text Field', 'iFrame Redirection', 'Using IP', 'Favicon',
        'Request URL', 'URL of Anchor', 'Links in Meta, Script, and Link tags', 'SFH (Server Form Handler)',
        'Submit Email', 'Redirect Count', 'OnMouseOver Changes Status',
        'Google Index', 'Domain Registration Length', 'Age Of Domain', 'DNS Record', 'SSLfinal State',
        'Having Sub Domain', 'HTTPS Token', 'Web Traffic', 'Page Rank', 'Links Pointing to Page', 'Statistical Report',
        'Shortening Service'
    ]

    # 피처 값을 올바른 순서로 정렬하여 데이터프레임으로 변환
    feature_values = [features[feature] for feature in feature_order]
    features_df = pd.DataFrame([feature_values], columns=feature_order)

    # 학습된 모델 로드
    with open('../model/mlp_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    # 피처 데이터프레임을 사용하여 예측 수행
    prediction = model.predict(features_df)[0]
    probability = model.predict_proba(features_df)[0]

    # 피싱 여부 및 상세 설명
    phishing = prediction == 1
    explanation = []

    for feature_name, feature_value in features.items():
        if feature_value == 1:
            explanation.append(f"{feature_name}: Suspicious")
    
    return phishing, probability[1], explanation

# 예시 URL
url = 'https://po.st/scam'  # 피싱, 단축 url

start_time = time.time()
phishing, probability, explanations = evaluate_url(url)
end_time = time.time()

print(f"URL: {url}")
print(f"피싱 확률: {probability:.2%}")
print(f"피싱 여부: {'Yes' if phishing else 'No'}")
if explanations:
    print("의심 피처들:")
    for explanation in explanations:
        print(f" - {explanation}")

print(f"분석 시간: {end_time - start_time:.2f} seconds")