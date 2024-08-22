import requests
from urllib.parse import urlparse
import urllib3


# 단축 URL 도메인 목록
SHORTENING_DOMAINS = set([
    'bit.ly', 'kl.am', 'cli.gs', 'bc.vc', 'po.st', 'v.gd', 'bkite.com',
    'shorl.com', 'scrnch.me', 'to.ly', 'adf.ly', 'x.co', '1url.com',
    'ad.vu', 'migre.me', 'su.pr', 'smallurl.co', 'cutt.us', 'filoops.info',
    'shor7.com', 'yfrog.com', 'tinyurl.com', 'u.to', 'ow.ly', 'ff.im',
    'rubyurl.com', 'r2me.com', 'post.ly', 'twitthis.com', 'buzurl.com',
    'cur.lv', 'tr.im', 'bl.lnk', 'tiny.cc', 'lnkd.in', 'q.gs', 'is.gd',
    'hurl.ws', 'om.ly', 'prettylinkpro.com', 'qr.net', 'qr.ae', 'snipurl.com',
    'ity.im', 't.co', 'db.tt', 'link.zip.net', 'doiop.com', 'url4.eu',
    'poprl.com', 'tweez.me', 'short.ie', 'me2.do', 'bit.do', 'shorte.st',
    'go2l.ink', 'yourls.org', 'wp.me', 'goo.gl', 'j.mp', 'twurl.nl',
    'snipr.com', 'shortto.com', 'vzturl.com', 'u.bb', 'shorturl.at',
    'han.gl', 'wo.gl', 'wa.gl', 'buly.kr', 'me2.kr' , 'url.kr'
])

def is_shortened_url(url):
    # 문제점 -> 단축 도메인에 없는 문자열은 확인이 불가함 -> 개선 필요
    """
    주어진 URL이 단축 URL인지 확인합니다.
    
    Args:
    - url (str): 검사할 URL
    
    Returns:
    - bool: 단축 URL이면 True, 그렇지 않으면 False
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc in SHORTENING_DOMAINS


def expand_shortened_url(url):
    # 문제점 피싱 단축 url의 경우 ssl, 보안 인증 등의 문제로 복원이 안됨 -> 아래 테스트 코드 참고
    """
    단축 URL을 복원합니다. HTTP와 HTTPS를 모두 시도
    
    Args:
    - url (str): 단축된 URL
    
    Returns:
    - str: 복원된 원본 URL (복원이 실패할 경우 기존 단축 url 반환)
    """
    try:
        # HTTPS 먼저 시도
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except requests.exceptions.Timeout:
        print(f"HTTPS 타임아웃 발생: {url}")
    except requests.exceptions.RequestException as e:
        print(f"HTTPS 복원 중 오류 발생: {e}")
    
    try:
        # HTTP로 재시도
        if url.startswith("https://"):
            url = url.replace("https://", "http://")
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except requests.exceptions.Timeout:
        print(f"HTTP 타임아웃 발생: {url}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP 복원 중 오류 발생: {e}")
    
    # 실패 시 기존 url 반환
    return url


def check_url(url):
    """
    입력된 URL이 단축 URL인지 확인 후 복원을 진행합니다.
    
    Args:
    - url (str): 검사할 URL
    
    Returns:
    - str: 원본 URL 또는 복원된 URL
    - int: 단축 URL이면 1, 일반 URL이면 -1
    """
    if is_shortened_url(url):
        print("단축 URL입니다.")
        expanded_url = expand_shortened_url(url)
        
        if expanded_url != url:
            print(f"복원된 URL: {expanded_url}")
            return expanded_url, 1
        else:
            print("복원에 실패하였습니다.")
            return url, -1
    else:
        print("일반 URL입니다.")
        return url, -1




# # # 테스트용 URL 목록
# test_urls = [
#   # 피싱 5개
#     'https://buly.kr/BITBije',
#     'https://buly.kr/9BU5wxI',
#     'https://buly.kr/Gkqg82e',
#     'https://buly.kr/GZvv9En',
#     'https://buly.kr/jXirow',

#     # 일반 5개
#    'https://buly.kr/2qWodcD',
#    'https://buly.kr/C08De2i',
#    'https://buly.kr/610SIJC',
#    'https://url.kr/b2ecua',
#    'https://tinyurl.com/3z5h4h3w',

#    # 단축 x -> 결과값 -1 예측
#    'https://naver.com'
#    ]

# # 테스트 수행
# for url in test_urls:
#     print(f"URL: {url}")
#     result = check_url(url)
#     print(f"결과: {result}\n")





# is_shorted_url test code
    # url1 = "https://www.example.com:8080/path/to/page?name=example#section"

    # parsed_url = urlparse(url1)
    # print(parsed_url)
# 결과 값 -> 여기서 netloc이 SHORTENING_DOMAINS에 있을 경우 단축 url이라고 판단
# ParseResult(scheme='https', netloc='www.example.com:8080', path='/path/to/page', params='', query='name=example', fragment='section')





# expand_shorted_url test code
#url = "https://po.st/scam"

# resp = requests.get(url)
# print(resp) 

# for respl in resp.history :
#     print(respl.headers)
#     print(respl.status_code, respl.url)
#     print()

# print(resp.headers)
# print(resp.status_code, resp.url)    

