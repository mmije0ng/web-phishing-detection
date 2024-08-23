import whois
import requests
from urllib.parse import urlparse
import datetime
import socket  # socket 모듈 임포트
import ssl  # ssl 모듈 임포트
from cryptography import x509  # x509 모듈 임포트
from cryptography.hazmat.backends import default_backend  # default_backend 임포트


# 피처 함수들 정의

def google_index(url):
    try:
        response = requests.get(f"https://www.google.com/search?q=site:{urlparse(url).netloc}")
        return 1 if 'No results' in response.text else -1  # 피싱이면 1, 정상이면 -1
    except requests.RequestException as e:
        print(f"Google Index Error: {e}")
        return 1  # 예외 발생 시 피싱으로 간주

# 도메인 등록 기간 (Domain_registration_length)
def domain_registration_length(url):
    try:
        # URL에서 도메인 추출
        domain = urlparse(url).netloc

        # 도메인 정보 가져오기
        domain_info = whois.whois(domain)

        # 도메인의 등록 만료일 추출
        expiration_date = domain_info.expiration_date

        # 등록 만료일이 리스트로 반환되는 경우 첫 번째 항목 선택
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        # 만료일이 없는 경우 피싱으로 간주
        if expiration_date is None:
            return 1

        # 현재 날짜와의 차이 계산
        remaining_days = (expiration_date - datetime.datetime.now()).days

        # 도메인 등록 기간이 1년(365일) 이상이면 정상, 그렇지 않으면 피싱
        return -1 if remaining_days >= 365 else 1

    except Exception as e:
        print(f"Domain Registration Length Error: {e}")
        return 1  # 오류 발생 시 피싱으로 간주

# 도메인 수명 (Age_of_Domain)
def age_of_domain(url):
    try:
        # URL에서 도메인 추출
        domain = urlparse(url).netloc

        # 도메인 정보 가져오기
        domain_info = whois.whois(domain)

        # 도메인의 생성일 추출
        creation_date = domain_info.creation_date

        # 생성일이 리스트로 반환되는 경우 첫 번째 항목 선택
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        # 생성일이 없는 경우 피싱으로 간주
        if creation_date is None:
            return 1

        # 도메인 나이 계산
        age_days = (datetime.datetime.now() - creation_date).days

        # 도메인 나이가 6개월(183일) 이상이면 정상, 그렇지 않으면 피싱
        return -1 if age_days >= 183 else 1

    except Exception as e:
        print(f"Age of Domain Error: {e}")
        return 1  # 오류 발생 시 피싱으로 간주

def dns_record(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        
        # 도메인 정보가 없거나 상태 정보가 없는 경우 피싱으로 간주
        if domain_info is None or domain_info.status is None:
            return 1  # 피싱
        
        return -1  # 정상
    except Exception as e:
        print(f"DNS Record Error: {e}")
        return 1  # 예외 발생 시 피싱으로 간주

# def ssl_certificate_status(url):
#     try:
#         response = requests.get(url, timeout=5)
#         return -1 if 'https' in response.url else 1  # 피싱이면 1, 정상이면 -1
#     except requests.RequestException as e:
#         print(f"SSL Certificate Status Error: {e}")
#         return 0  # 의심
#     except Exception as e:
#         print(f"SSL Certificate Status General Error: {e}")
#         return 0  # 의심

def sslfinal_state(url):
    # 1. HTTPS 사용 여부 확인
    if not url.startswith("https://"):
        return 1  # 피싱 사이트 (HTTPS를 사용하지 않음)
    
    try:
        # 2. SSL 인증서 정보 가져오기
        hostname = url.split("://")[1].split('/')[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # 3. 인증서 발급자 확인
        issuer = dict(x[0] for x in cert['issuer'])
        trusted_issuers = ["Let's Encrypt", "DigiCert", "GlobalSign", "Comodo", "Symantec"]  # 신뢰할 수 있는 발급자 목록
        
        if issuer.get('organizationName', '') in trusted_issuers:
            trusted = True
        else:
            trusted = False

        # 4. 인증서 기간 확인
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        period = (not_after - datetime.datetime.utcnow()).days
        
        if trusted and period >= 365:
            return -1  # 정상이면 -1 반환
        elif not trusted or period < 365:
            return 0  # 의심스러운 경우 0 반환
        else:
            return 1  # 피싱 사이트 (기타 경우)
    except Exception as e:
        print(f"SSL Certificate Status Error: {e}")
        return 1  # 피싱 사이트 (오류 발생 시)
    
def having_subdomain(url):
    try:
        netloc = urlparse(url).netloc
        # 도메인 부분을 점(.)으로 분리
        parts = netloc.split('.')
        
        # 서브도메인 개수 계산
        # TLD와 주 도메인을 제외한 부분이 서브도메인
        if len(parts) <= 2:
            return -1  # 서브도메인이 없음 (정상)
        elif len(parts) == 3:
            return 0  # 서브도메인 1개 (의심)
        else:
            return 1  # 서브도메인 2개 이상 (피싱)
    except Exception as e:
        print(f"Having Subdomain Error: {e}")
        return 0  # 예외 발생 시 의심


def https_token(url):
    try:
        # URL에서 도메인 부분을 추출
        domain = urlparse(url).netloc
        
        # 도메인 부분에 "https-" 토큰이 포함되어 있는지 확인
        if "https-" in domain.lower():
            return 1  # 피싱
        else:
            return -1  # 정상
    except Exception as e:
        # 예외 발생 시 피싱으로 간주
        print(f"HTTPS Token Error: {e}")
        return 1  # 피싱

def web_traffic(url):
    try:
        return 1 if "low-traffic" in url else -1  # 피싱이면 1, 정상이면 -1
    except Exception as e:
        print(f"Web Traffic Error: {e}")
        return 0  # 의심

def check_url(url):
    results = {}
    results['Google_Index'] = google_index(url)
    results['Domain_registeration_length'] = domain_registration_length(url)
    results['age_of_domain'] = age_of_domain(url)
    results['DNSRecord'] = dns_record(url)
    results['SSLfinal_State'] = sslfinal_state(url)
    results['having_Sub_Domain'] = having_subdomain(url)
    results['HTTPS_token'] = https_token(url)
    results['web_traffic'] = web_traffic(url)

    score = sum(int(value) for value in results.values())

    if score > 0:
        results['Phishing_Site'] = "Yes"
    elif score == 0:
        results['Phishing_Site'] = "Suspicious"
    else:
        results['Phishing_Site'] = "No"

    return results

# 테스트할 URL 목록
urls = [
    "http://www.crestonwood.com/router.php",
    "http://shadetreetechnology.com/V4/validation/a111aedc8ae390eabcfa130e041a10a4",
    "https://support-appleld.com.secureupdate.duilawyeryork.com/ap/89e6a3b4b063b8d/?cmd=_update&dispatch=89e6a3b4b063b8d1b&locale=_",
    "http://rgipt.ac.in",
    "http://www.iracing.com/tracks/gateway-motorsports-park/",
    "http://appleid.apple.com-app.es/",
    "http://www.mutuo.it",
    "http://www.shadetreetechnology.com/V4/validation/ba4b8bddd7958ecb8772c836c2969531",
    "http://vamoaestudiarmedicina.blogspot.com/",
    "https://parade.com/425836/joshwigler/the-amazing-race-host-phil-keoghan-previews-the-season-27-premiere/",
]

for url in urls:
    result = check_url(url)
    print(f"URL: {url}")
    print(result)
    print("-" * 80)
