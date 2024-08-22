import whois
import requests
from urllib.parse import urlparse
import datetime


# 피처 함수들 정의

def google_index(url):
    try:
        response = requests.get(f"https://www.google.com/search?q=site:{urlparse(url).netloc}")
        return -1 if 'No results' not in response.text else 1
    except requests.RequestException as e:
        print(f"Google Index Error: {e}")
        return 0  # 의심

def domain_registration_period(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return 0  # 의심
        age_days = (datetime.datetime.now() - creation_date).days
        return 1 if age_days < 180 else -1
    except Exception as e:
        print(f"Domain Registration Period Error: {e}")
        return 0  # 의심

def domain_age(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return 0  # 의심
        age_days = (datetime.datetime.now() - creation_date).days
        #도메인 등록 기간이 6개월 미만인 경우에 피싱사이트로 간주
        return 1 if age_days < 183 else -1
    except Exception as e:
        print(f"Domain Age Error: {e}")
        return 0  # 의심

def dns_record(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        if domain_info is None or domain_info.status is None:
            return 1  # 피싱
        return -1  # 정상
    except Exception as e:
        print(f"DNS Record Error: {e}")
        return 0  # 의심

def ssl_certificate_status(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if 'https' in response.url else 1  # 피싱이면 1, 정상이면 -1
    except requests.RequestException as e:
        print(f"SSL Certificate Status Error: {e}")
        return 0  # 의심
    except Exception as e:
        print(f"SSL Certificate Status General Error: {e}")
        return 0  # 의심

# def having_subdomain(url):
#     try:
#         subdomain_count = urlparse(url).netloc.count('.')
#         return 1 if subdomain_count > 1 else -1  # 피싱이면 1, 정상이면 -1
#     except Exception as e:
#         print(f"Having Subdomain Error: {e}")
#         return 0  # 의심


# def having_subdomain(url):
#     try:
#         subdomain_count = urlparse(url).netloc.count('.')
#         if subdomain_count == 0:
#             return -1  # 정상 (legitimate)
#         elif subdomain_count == 1:
#             return 0  # 의심 (suspicious)
#         else:
#             return 1  # 피싱 (phishing)
#     except Exception as e:
#         print(f"Having Subdomain Error: {e}")
#         return 0  # 의심 (suspicious)
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


# def https_token(url):
#     try:
#         return 1 if 'https-' in url else -1  # 피싱이면 1, 정상이면 -1
#     except Exception as e:
#         print(f"HTTPS Token Error: {e}")
#         return 0  # 의심
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
        # 예외 발생 시 의심으로 간주
        print(f"HTTPS Token Error: {e}")
        return 0  # 의심

def web_traffic(url):
    try:
        return 1 if "low-traffic" in url else -1  # 피싱이면 1, 정상이면 -1
    except Exception as e:
        print(f"Web Traffic Error: {e}")
        return 0  # 의심

def check_url(url):
    results = {}
    results['Google_Index'] = google_index(url)
    results['Domain_registeration_length'] = domain_registration_period(url)
    results['age_of_domain'] = domain_age(url)
    results['DNSRecord'] = dns_record(url)
    results['SSLfinal_State'] = ssl_certificate_status(url)
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

# # 테스트할 URL 목록
# urls = [
#     "http://www.crestonwood.com/router.php",
#     "http://shadetreetechnology.com/V4/validation/a111aedc8ae390eabcfa130e041a10a4",
#     "https://support-appleld.com.secureupdate.duilawyeryork.com/ap/89e6a3b4b063b8d/?cmd=_update&dispatch=89e6a3b4b063b8d1b&locale=_",
#     "http://rgipt.ac.in",
#     "http://www.iracing.com/tracks/gateway-motorsports-park/",
#     "http://appleid.apple.com-app.es/",
#     "http://www.mutuo.it",
#     "http://www.shadetreetechnology.com/V4/validation/ba4b8bddd7958ecb8772c836c2969531",
#     "http://vamoaestudiarmedicina.blogspot.com/",
#     "https://parade.com/425836/joshwigler/the-amazing-race-host-phil-keoghan-previews-the-season-27-premiere/",
# ]

# for url in urls:
#     result = check_url(url)
#     print(f"URL: {url}")
#     print(result)
#     print("-" * 80)
