import pandas as pd
from urllib.parse import urlparse

# 블랙리스트 데이터를 읽어옵니다.
shortened_urls_df = pd.read_csv('features/filtered_short_urls.csv')

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
    주어진 URL이 단축 URL인지 확인.
    
    Args:
    - url (str): 검사할 URL
    
    Returns:
    - bool: 단축 URL이면 True, 그렇지 않으면 False
    """
    parsed_url = urlparse(url)
    if parsed_url.netloc in SHORTENING_DOMAINS:
        print(1)  # 단축 URL일 때 1 출력
        return 1
    else:
        print(-1)  # 단축 URL이 아닐 때 -1 출력
        return -1

def check_phishing_shortening_service(url):
    """
    주어진 URL이 단축 URL인지 확인하고, 블랙리스트에 있는지 검사.
    
    Args:
    - url (str): 검사할 URL
    
    Returns:
    - int: -1 (정상 사이트), 1 (피싱 사이트), -1 (단축 URL 아님)
    """
    parsed_url = urlparse(url)
    
    # 단축 URL인지 확인
    if not is_shortened_url(url):
        print('not a shortened URL')
        return -1
    
    # 스킴을 제외한 나머지 부분 (도메인 + 경로)을 추출
    full_url_without_scheme = parsed_url.netloc + parsed_url.path
    print('Full URL without scheme: ' + full_url_without_scheme)

    # 해당 URL이 블랙리스트에 있는지 검사
    matching_row = shortened_urls_df[shortened_urls_df['url'] == full_url_without_scheme]

    if not matching_row.empty:
        # 해당 URL이 존재하면, 라벨을 확인
        label = matching_row['label'].values[0]
        print("label: " + label)
        if label == 'good':
            return -1  # 정상 사이트
        elif label == 'bad':
            return 1  # 피싱 사이트
    else:
        # 해당 URL이 존재하지 않은 경우
        print('URL not found in blacklist')
        return -1

# 테스트 URL
if __name__ == "__main__":
    example_url = 'https://goo.gl/EKpJ8k'
    result = check_phishing_shortening_service(example_url)
    print(result)  # -1 (정상), 1 (피싱), -1 (단축 URL 아님)