import asyncio
from features import short_url_features, url_based_feature, content_based_features, domain_based_features
from entity.models import Features
import numpy as np
import time
from sqlalchemy.exc import IntegrityError

# 피처 이름 목록을 모델 학습 데이터의 피처 순서와 일치시킴
FEATURE_ORDER = [
    'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service', 'having_At_Symbol', 'double_slash_redirecting',
    'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State', 'Favicon',
    'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
    'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain', 'Google_Index'
]

# URL 기반 피처 목록
URL_BASED_FEATURES = [
    'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service',
    'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix'
]

# 컨텐츠 기반 피처 목록
CONTENT_BASED_FEATURES = [
    'RightClick', 'popUpWidnow', 'Iframe', 'Favicon', 'Request_URL',
    'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
    'Redirect', 'on_mouseover'
]

# 도메인 기반 피처 목록
DOMAIN_BASED_FEATURES = [
    'Google_Index', 'age_of_domain', 'SSLfinal_State', 'having_Sub_Domain',
    'HTTPS_token'
]

# 피처 추출 함수
async def extract_features(url):
    """URL에서 피처를 비동기로 추출하여 반환하는 함수."""
    
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
    feature_values = [features[feature] for feature in FEATURE_ORDER]
    
    return np.array(feature_values).reshape(1, -1), features

def get_suspicious_features(features):
    """피처 딕셔너리에서 값이 1인 의심 피처를 URL, Content, Domain 기반으로 나누어 반환하는 함수."""

    suspicious_url_based = []
    suspicious_content_based = []
    suspicious_domain_based = []
    
    # URL 기반 피처 확인
    for feature_name in URL_BASED_FEATURES:
        if features.get(feature_name, 0) == 1:
            suspicious_url_based.append(feature_name)

    # Content 기반 피처 확인
    for feature_name in CONTENT_BASED_FEATURES:
        if features.get(feature_name, 0) == 1:
            suspicious_content_based.append(feature_name)

    # Domain 기반 피처 확인
    for feature_name in DOMAIN_BASED_FEATURES:
        if features.get(feature_name, 0) == 1:
            suspicious_domain_based.append(feature_name)

    # 각 그룹의 의심 피처들을 사전 형태로 반환
    return {
        "URL_based": suspicious_url_based,
        "Content_based": suspicious_content_based,
        "Domain_based": suspicious_domain_based
    }


# Features 테이블에 피처 추가 또는 업데이트하는 함수
def add_or_update_features_entity(db, url_id, features):
    """
    Features 테이블에 피처 값을 추가하거나 업데이트하는 함수.
    
    Args:
        db: 데이터베이스 세션 객체.
        url_id: URLs 테이블의 url_id.
        features: 추출된 피처 값들.
    """
    try:
        # Features 테이블에서 해당 URL에 대한 피처가 이미 있는지 확인
        features_entity = Features.query.filter_by(url_id=url_id).first()

        if features_entity:
            # 이미 존재하는 경우 업데이트
            features_entity.having_ip_address = features['having_IPhaving_IP_Address']
            features_entity.url_length = features['URLURL_Length']
            features_entity.shortening_service = features['Shortining_Service']
            features_entity.having_at_symbol = features['having_At_Symbol']
            features_entity.double_slash_redirecting = features['double_slash_redirecting']
            features_entity.prefix_suffix = features['Prefix_Suffix']
            features_entity.having_sub_domain = features['having_Sub_Domain']
            features_entity.ssl_final_state = features['SSLfinal_State']
            features_entity.favicon = features['Favicon']
            features_entity.port = features['port']
            features_entity.https_token = features['HTTPS_token']
            features_entity.request_url = features['Request_URL']
            features_entity.url_of_anchor = features['URL_of_Anchor']
            features_entity.links_in_tags = features['Links_in_tags']
            features_entity.sfh = features['SFH']
            features_entity.submitting_to_email = features['Submitting_to_email']
            features_entity.redirect = features['Redirect']
            features_entity.on_mouseover = features['on_mouseover']
            features_entity.right_click = features['RightClick']
            features_entity.popup_window = features['popUpWidnow']
            features_entity.iframe = features['Iframe']
            features_entity.age_of_domain = features['age_of_domain']
            features_entity.google_index = features['Google_Index']

            print(f"Features updated for URL ID {url_id}")
        else:
            # 레코드가 없을 경우 새로 추가
            new_features = Features(
                url_id=url_id,
                having_ip_address=features['having_IPhaving_IP_Address'],
                url_length=features['URLURL_Length'],
                shortening_service=features['Shortining_Service'],
                having_at_symbol=features['having_At_Symbol'],
                double_slash_redirecting=features['double_slash_redirecting'],
                prefix_suffix=features['Prefix_Suffix'],
                having_sub_domain=features['having_Sub_Domain'],
                ssl_final_state=features['SSLfinal_State'],
                favicon=features['Favicon'],
                port=features['port'],
                https_token=features['HTTPS_token'],
                request_url=features['Request_URL'],
                url_of_anchor=features['URL_of_Anchor'],
                links_in_tags=features['Links_in_tags'],
                sfh=features['SFH'],
                submitting_to_email=features['Submitting_to_email'],
                redirect=features['Redirect'],
                on_mouseover=features['on_mouseover'],
                right_click=features['RightClick'],
                popup_window=features['popUpWidnow'],
                iframe=features['Iframe'],
                age_of_domain=features['age_of_domain'],
                google_index=features['Google_Index']
            )
            db.session.add(new_features)
            print(f"New features added for URL ID {url_id}")

        # 데이터베이스 커밋
        db.session.commit()

    except IntegrityError as e:
        # 오류 발생 시 세션 롤백 및 오류 메시지 출력
        db.session.rollback()
        print(f"Error occurred while saving/updating features for URL ID {url_id}: {e}")

# # update
# # Features 테이블에 피처 추가/업데이트하는 함수
# def update_features_entity(db, url_id, features):
#     """
#     Features 테이블에 피처 값을 업데이트하거나 새로 추가하는 함수.
    
#     Args:
#         db: 데이터베이스 세션 객체.
#         url_id: URLs 테이블의 url_id.
#         features: 추출된 피처 값들.
#     """
#     try:
#         # Features 테이블에서 해당 URL에 대한 피처가 이미 있는지 확인
#         features_entity = Features.query.filter_by(url_id=url_id).first()

#         # 이미 존재하는 경우 업데이트
#         features_entity.having_ip_address = features['having_IPhaving_IP_Address']
#         features_entity.url_length = features['URLURL_Length']
#         features_entity.shortening_service = features['Shortining_Service']
#         features_entity.having_at_symbol = features['having_At_Symbol']
#         features_entity.double_slash_redirecting = features['double_slash_redirecting']
#         features_entity.prefix_suffix = features['Prefix_Suffix']
#         features_entity.having_sub_domain = features['having_Sub_Domain']
#         features_entity.ssl_final_state = features['SSLfinal_State']
#         features_entity.favicon = features['Favicon']
#         features_entity.port = features['port']
#         features_entity.https_token = features['HTTPS_token']
#         features_entity.request_url = features['Request_URL']
#         features_entity.url_of_anchor = features['URL_of_Anchor']
#         features_entity.links_in_tags = features['Links_in_tags']
#         features_entity.sfh = features['SFH']
#         features_entity.submitting_to_email = features['Submitting_to_email']
#         features_entity.redirect = features['Redirect']
#         features_entity.on_mouseover = features['on_mouseover']
#         features_entity.right_click = features['RightClick']
#         features_entity.popup_window = features['popUpWidnow']
#         features_entity.iframe = features['Iframe']
#         features_entity.age_of_domain = features['age_of_domain']
#         features_entity.google_index = features['Google_Index']

#         # 데이터베이스 커밋
#         db.session.commit()
#         print(f"Features updated for URL ID {url_id}")

#     except IntegrityError as e:
#         db.session.rollback()
#         print(f"Error occurred while adding/updating features for URL ID {url_id}: {e}")

# # add

# # Features 테이블 저장
# def add_features_entity(db, url_id, features):
#     print("ip: "+features['having_IPhaving_IP_Address'])

#     new_features = Features(
#         url_id=url_id,
#         having_ip_address=features['having_IPhaving_IP_Address'],
#         url_length=features['URLURL_Length'],
#         shortening_service=features['Shortining_Service'],
#         having_at_symbol=features['having_At_Symbol'],
#         double_slash_redirecting=features['double_slash_redirecting'],
#         prefix_suffix=features['Prefix_Suffix'],
#         having_sub_domain=features['having_Sub_Domain'],
#         ssl_final_state=features['SSLfinal_State'],
#         favicon=features['Favicon'],
#         port=features['port'],
#         https_token=features['HTTPS_token'],
#         request_url=features['Request_URL'],
#         url_of_anchor=features['URL_of_Anchor'],
#         links_in_tags=features['Links_in_tags'],
#         sfh=features['SFH'],
#         submitting_to_email=features['Submitting_to_email'],
#         redirect=features['Redirect'],
#         on_mouseover=features['on_mouseover'],
#         right_click=features['RightClick'],
#         popup_window=features['popUpWidnow'],
#         iframe=features['Iframe'],
#         age_of_domain=features['age_of_domain'],
#         google_index=features['Google_Index']
#     )

#     # 새 피처 데이터베이스에 추가
#     db.session.add(new_features)
#     print(f"New features added for URL ID {url_id}")
