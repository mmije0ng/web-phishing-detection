from entity.models import URLs
from service import feature_service, predict_service, blacklist_service
from dto import url_response_dto, error_response_dto
import time
import dns.resolver
from urllib.parse import urlparse
import dns.message
import dns.query
import requests
import config
from exceptions import DomainToIPError

API_KEY = config.API_KEY    

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

# URLs 테이블 존재 여부 반환
def get_url_exist(url):
    # 기존 URL이 있는지 확인
    existing_url = URLs.query.filter_by(url=url).first()
    url_exist=True
    
    if existing_url:
        # URL이 존재하면 True와 해당 URL의 url_id를 반환
        return url_exist, existing_url.url_id
    else:
        # URL이 존재하지 않으면 False를 반환
        url_exist=False
        return url_exist, None

# 확장용 분석 결과
async def simple_analyze_url(db, url):
    """URL에 대해 피처 추출 및 분석을 실행하는 함수."""

    start_time = time.time()

    url_id = get_url_id(db, url) # URLs 테이블 존재 여부에 따른 url_id 반환
        
    # 피처 추출
    features_array, features = await feature_service.extract_features(url)
        
    # 피싱 여부 및 확률 예측
    phishing_result, phishing_prob = predict_service.predict_phishing(features_array)

    # #DB 저장
    # # URLs 테이블에서 해당 URL이 존재하는지 확인
    # url_exist, url_id = get_url_exist(url)

    # if url_exist:
    #     # URL이 존재하면 search_count 증가
    #     update_urls_entity(db, url_id)
    # else:
    #     # URL이 존재하지 않으면 새로운 URL 추가
    #     url_id=add_urls_entity(db, url)



    # url_entry = URLs.query.filter_by(url=url).first() # URLs에 있는지 검색

    # if not url_entry:
    #     # URLs에 존재하지 않으면 새로 생성 후 DB 조작
    #     new_url_entry = URLs(url=url, search_count=1)
    #     db.session.add(new_url_entry)
    #     db.session.commit()
    
    feature_service.add_or_update_features(db, url_id, features)
    predict_service.add_or_update_predictions(db, url_id, phishing_result, phishing_prob)

    blacklist_service.add_to_blacklist(db, url) # search_count >= 20시, 블랙리스트 추가
        
    # DTO 생성
    simple_response_dto = url_response_dto.SimpleResponseDTO(url, phishing_result, phishing_prob)
        
    # 결과 출력
    print(f"Simple Response DTO: {simple_response_dto}")
        
    print("-" * 50)

    # 실행 시간 출력
    elapsed_time = time.time() - start_time
    print(f"실행 시간: {elapsed_time:.4f}초\n")

    return simple_response_dto

# 웹용 분석 결과
async def detailed_analyze_url(db, url):
    """URL에 대해 피처 추출 및 분석을 실행하는 함수."""
    
    start_time = time.time()

    # URL ID 가져오기 또는 생성
    url_id = get_url_id(db, url)

    blacklist_info = blacklist_service.check_blacklist(db, url) # URLs 테이블에서 URL이 블랙리스트에 있는지 확인
    
    # 블랙리스트에 있다면 Features 테이블에서 의심 피처와 Blacklist 테이블에서 결과, 확률 추출
    if blacklist_info:
        print(f"{url} 블랙리스트 존재")
        suspicious_features = feature_service.extract_suspicious_features_from_db(db, url_id)
        prediction_result = blacklist_info.b_result
        prediction_prob = blacklist_info.b_prob

    else:
        blacklist_service.add_to_blacklist(db, url) # search_count >= 20시, 블랙리스트 추가

        # 피처 추출
        features_array, features = await feature_service.extract_features(url)
            
        # 피싱 여부 및 확률 예측
        prediction_result, prediction_prob = predict_service.predict_phishing(features_array)
        
        # features, predicts 테이블 업데이트
        feature_service.add_or_update_features(db, url_id, features)
        predict_service.add_or_update_predictions(db, url_id, prediction_result, prediction_prob)

        # 의심 피처 추출
        suspicious_features = feature_service.get_suspicious_features(features)

    # IP 주소로 도메인 변환 시도 및 상세 정보 가져오기
    try:
        ip_address = change_domain_to_ip(url)
        ip_info = get_detailed_response_by_ip(ip_address)
    except DomainToIPError as e:
        print(f"DomainToIPError 에러 발생: {str(e)}")
        ip_info = {
            "ip_address": "N/A",
            "country": "N/A",
            "region": "N/A",
            "is_vpn": "N/A",
            "isp_name": "N/A"
        }

    # 응답 DTO 생성
    detailed_response_dto = url_response_dto.DetailedResponseDTO(
        url, prediction_result, prediction_prob, suspicious_features, ip_info
    )
    
    # 실행 시간 출력
    elapsed_time = time.time() - start_time
    print(f"실행 시간: {elapsed_time:.4f}초\n")

    return detailed_response_dto

def change_domain_to_ip(url):
    try:
        # URL에서 도메인 추출
        domain = urlparse(url).netloc
        print("도메인: " + domain)

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
            raise DomainToIPError(f"{domain}에 대한 IP 주소를 찾을 수 없습니다.")

        return ip_address

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise  # 발생한 에러를 최상위 메서드로 전달


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
        region = data.get("region", "N/A")
        is_vpn = data.get("security", {}).get("is_vpn", "N/A")
        isp_name = data.get("connection", {}).get("isp_name", "N/A")

        # 추출한 정보 출력
        print(f"IP 주소: {ip}")
        print(f"국가: {country}")
        print(f"지역: {region}")
        print(f"VPN 사용 여부: {is_vpn}")
        print(f"ISP 이름: {isp_name}")

        # 필요한 데이터를 딕셔너리로 반환
        return {
            "ip_address": ip,
            "country": country,
            "region": region,
            "is_vpn": is_vpn,
            "isp_name": isp_name
        }

    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        return None


# # URLs 테이블 업데이트
# def update_urls_entity(db, url_id):
#     # 기존 URL이 있는지 확인
#     url_entity = URLs.query.filter_by(url_id=url_id).first()
    
#     # URL이 이미 존재하면 search_count 값을 1 증가
#     url_entity.search_count += 1
#     print(f"Existing URL found. search_count updated to: {url_entity.search_count}")
    
#     # 세션에 데이터가 있는지 확인
#     print("Session pending changes:", db.session.new)
    
#     # 데이터베이스에 커밋
#     db.session.commit()  
#     print("URLs update successfully") 

# # URLs 테이블 저장
# def add_urls_entity(db, url):
#     # URL 객체 생성
#     new_url_entity = URLs(url=url)
    
#     # 세션에 URL 객체 추가
#     db.session.add(new_url_entity)
#     print(f"New URL added: {url}")
    
#     # 세션에 데이터가 있는지 확인
#     print("Session pending changes:", db.session.new)
    
#     # 데이터베이스에 커밋
#     db.session.commit()
#     print("URLs saved successfully")
    
#     # 커밋 후 url_entity의 url_id 반환
#     return new_url_entity.url_id
