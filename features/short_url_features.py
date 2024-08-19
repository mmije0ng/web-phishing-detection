import requests
from urllib.parse import urlparse

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
    'han.gl', 'wo.gl', 'wa.gl'
])

def is_shortened_url(url):
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
    """
    단축 URL을 원본 URL로 복원합니다.
    
    Args:
    - url (str): 단축된 URL
    
    Returns:
    - str: 원본 URL
    """
    try:
        # requests 라이브러리를 사용하여 URL 복원, 타임아웃 5초로 설정
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.url
    except requests.exceptions.Timeout:
        print(f"URL 복원 중 오류 발생: 타임아웃이 발생했습니다. ({url})")
        return None
    except requests.exceptions.RequestException as e:
        print(f"URL 복원 중 오류 발생: {e}")
        return None

def check_url(url):
    """
    URL을 분석하고 단축 URL이면 복원 후 피싱 여부를 판단합니다.
    
    Args:
    - url (str): 검사할 URL
    
    Returns:
    - str: '정상 사이트' 또는 '피싱 사이트'
    """
    if is_shortened_url(url):
        print("단축 URL입니다. 원본 URL로 복원 중...")
        expanded_url = expand_shortened_url(url)
        
        if expanded_url:
            print(f"복원된 URL: {expanded_url}")
            # 이 부분은 주석 처리합니다
            # return team_members_phishing_check(expanded_url)  # 다른 팀원이 작성한 함수
            # return "복원된 URL을 확인했습니다."
            return expanded_url, 1
        else:
            # return "복원 실패: URL을 확인할 수 없습니다."
            return url, -1
    else:
        print("일반 URL입니다.")
        # 이 부분은 주석 처리합니다
        # return team_members_phishing_check(url)  # 다른 팀원이 작성한 함수
        # return "일반 URL을 확인했습니다."
        return url, -1

# # 테스트용 URL 목록
# test_urls = [
#     # 단축 URL (정상 5개, 악성 5개)
#     'https://bit.ly/3xyz123',  # 정상
#     'https://tinyurl.com/y6abcd',  # 정상
#     'https://goo.gl/abc123',  # 정상
#     'https://ow.ly/abcd1234',  # 정상
#     'https://bit.ly/4abcd',  # 정상
#     'https://bit.ly/malicious1',  # 악성
#     'https://cli.gs/malware',  # 악성
#     'https://v.gd/phishing',  # 악성
#     'https://bc.vc/fraud',  # 악성
#     'https://po.st/scam',  # 악성

#     # 일반 URL (정상 5개, 악성 5개)
#     'https://www.google.com',  # 정상
#     'https://www.wikipedia.org',  # 정상
#     'https://www.python.org',  # 정상
#     'https://www.github.com',  # 정상
#     'https://www.stackoverflow.com',  # 정상
#     'http://malicious-site.com',  # 악성
#     'http://phishing-site.com',  # 악성
#     'http://fraud-site.org',  # 악성
#     'http://fake-login.net',  # 악성
#     'http://dangerous-site.biz',  # 악성
# ]

# # 테스트 수행
# for url in test_urls:
#     print(f"URL: {url}")
#     result = check_url(url)
#     print(f"결과: {result}\n")
