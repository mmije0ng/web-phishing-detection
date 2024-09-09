from entity.models import URLs
from service import feature_service, predict_service
from dto import url_response_dto
import time
import dns.resolver
from urllib.parse import urlparse
import dns.message
import dns.query
import requests
import config

API_KEY = config.API_KEY

def not_blacklist_detailed_analyze_url(db, url):
    url_id = get_url_id(db, url)
    return detailed_analyze_url(db, url, url_id)

# URL ID를 확인하고 없으면 생성하는 함수
def get_url_id(db, url):
    existing_url = URLs.query.filter_by(url=url).first()

    if existing_url:
        update_urls_entity(db, existing_url)
        return existing_url.url_id
    else:
        return add_urls_entity(db, url)

# URLs 테이블 search_count 증가 update
def update_urls_entity(db, url_entity):
    url_entity.search_count += 1
    print(f"Existing URL found. search_count updated to: {url_entity.search_count}")
    commit_db_changes(db)

# URLs 테이블에 URL 추가 후 ID 반환
def add_urls_entity(db, url):
    new_url_entity = URLs(url=url)
    db.session.add(new_url_entity)
    print(f"New URL added: {url}")
    commit_db_changes(db)
    return new_url_entity.url_id

# 데이터베이스 변경사항 커밋
def commit_db_changes(db):
    print("Session pending changes:", db.session.new)
    db.session.commit()
    print("Database changes committed successfully")


# (웹용) 상세 분석 결과
async def detailed_analyze_url(db, url, url_id):
    """URL에 대해 피처 추출 및 분석을 실행하는 함수."""

    start_time = time.time()
        
    # 피처 추출
    features_array, features = await feature_service.extract_features(url)
        
    # 피싱 여부 및 확률 예측
    prediction_result, prediction_prob = predict_service.predict_phishing(features_array)
    
    # features, predicts 테이블 업데이트
    feature_service.add_or_update_features(db, url_id, features)
    predict_service.add_or_update_predictions(db, url_id, prediction_result, prediction_prob)

    # 의심 피처 추출
    suspicious_features = feature_service.get_suspicious_features(features)
        
    ip_address = change_domain_to_ip(url) # DNS를 이용하여 Domain => IP로 변환
    ip_info = get_detailed_response_by_ip(ip_address) # API를 이용하여 IP를 기반으로 상세 정보를 받아옴

    # DTO 생성
    detailed_response_dto = url_response_dto.detailed_response_dto(url, prediction_result, prediction_prob, suspicious_features, ip_info)
        
    # 결과 출력
    print(f"Detailed Response DTO: {detailed_response_dto}")
        
    print("-" * 50)

    # 실행 시간 출력
    elapsed_time = time.time() - start_time
    print(f"실행 시간: {elapsed_time:.4f}초\n")

    return detailed_response_dto


# url에서 도메인을 추출하여 ip로 변환
def change_domain_to_ip(url):
    # URL에서 도메인 추출
    domain = urlparse(url).netloc

    # 사용할 DNS Server 주소 입력 (Google Public DNS 서버)
    dns_server = '8.8.8.8'

    # 도메인의 A record에 대한 DNS 쿼리 생성
    query = dns.message.make_query(domain, 'A')

    # DNS 서버로 쿼리 전송 및 응답 받기
    response = dns.query.udp(query, dns_server)

    # 응답으로부터 A 레코드(IP 주소) 추출
    ip_addresses = []
    for answer in response.answer:
        for item in answer.items:
            if item.rdtype == dns.rdatatype.A:  # A 레코드만 필터링
                ip_addresses.append(item.address)

    # 첫 번째 IP 주소만 반환
    if ip_addresses:
        ip_address = ip_addresses[0]
        print(f"{domain}의 IP 주소는 {ip_address}입니다.")
    else:
        ip_address = None
        print(f"{domain}에 대한 IP 주소를 찾을 수 없습니다.")

    print("IP 주소: " + str(ip_address))
    return ip_address


# ip를 기반으로 정보 가져오기
def get_detailed_response_by_ip(ip_address): 
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={API_KEY}&ip_address={ip_address}"
    
    # API 요청 보내기
    response = requests.get(url)

    # 응답 상태 코드가 200일 때 JSON 응답 처리
    if response.status_code == 200:
        data = response.json()

        # 필요한 필드 추출
        ip = data.get("ip_address", "N/A")
        country = data.get("country", "N/A")
        is_vpn = data.get("security", {}).get("is_vpn", "N/A")
        isp_name = data.get("connection", {}).get("isp_name", "N/A")

        # 추출한 정보 출력
        print(f"IP 주소: {ip}")
        print(f"국가: {country}")
        print(f"VPN 사용 여부: {is_vpn}")
        print(f"ISP 이름: {isp_name}")

        # 필요한 데이터를 딕셔너리로 반환
        return {
            "ip_address": ip,
            "country": country,
            "is_vpn": is_vpn,
            "isp_name": isp_name
        }

    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        return None