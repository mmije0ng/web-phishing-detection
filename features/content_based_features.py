import requests
import re
import regex
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

# 피싱 1, 정상 -1, 의심 0

# URL 데이터 추출
def get_request_url(url):
    try:
        response = requests.get(url, timeout=5)  # 웹 페이지의 HTML 소스를 받아옴
        return response
        
    except requests.RequestException as e:
        print("HTTP 요청 Error: {e}")
        return None   

# 도메인 추출 함수
def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# RightClick
# 우클릭 방지 여부
def use_right_click(response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        
        # 응답 텍스트가 비어 있는 경우 피싱으로 간주
        if response.text.strip() == "":
            return 1  
        else:
            # 마우스 우클릭이 비활성화 되어 있다면 피싱
            if regex.findall(r"event\.button ?== ?2", response.text):
                return 1  # Contains right-click disabling code, likely phishing
            # 마우스 우클릭이 활성화 되어 있다면 정상
            else:
                return -1
        
    except requests.RequestException as e:
        print(f"RightClick HTTP 요청 Error: {e}")
        return 0  # 요청 오류로 인해 사이트를 확인할 수 없을 시 의심으로 간주
    except Exception as e:
        print(f"RightClick Exception Error: {e}")
        return 0  # 에러 발생 시 의심으로 간주 


# popUpWidnow    
# 팝업 창에 텍스트 필드가 포함되어 있는지 여부
def popup_window_text(response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        
        soup = BeautifulSoup(response.content, 'lxml')
        forms = soup.find_all('form')
        
        # 텍스트 필드 포함 시 피싱
        if any(form.find('input', {'type': 'text'}) for form in forms):
            return 1  
        # 텍스트 필드 미포함시 정상 
        else: 
            return -1 
        
    except requests.RequestException as e:
        print(f"popUpWidnow HTTP 요청 Error: {e}")
        return 0 
    except Exception as e:
        print(f"popUpWidnow Exception Error: {e}")
        return 0

# Iframe
# iframe 사용 여부
def iFrame_redirection(response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # 응답의 텍스트가 비어 있는 경우 피싱으로 간주
        if response.text.strip() == "":
            return 1
        
        # 페이지 텍스트에서 파이프 문자가 있는지 확인
        if re.search(r"\|", response.text):
            return -1  # 파이프 문자가 있으면 정상 웹사이트로 간주
        
        # 파이프 문자가 없으면 피싱으로 간주
        return 1
            
    except requests.RequestException as e:
        print(f"Iframe HTTP 요청 Error: {e}")
        return 0
    except Exception as e:
        print(f"Iframe Exception Error: {e}")
        return 0  

# having_IPhaving_IP_Address
# IP 사용 여부
def using_ip(url):
    domain = extract_domain(url)
    # IP 주소를 직접 사용하면 피싱일 가능성이 있음
    return 1 if domain.replace('.', '').isdigit() else -1

# Favicon
# favicon 사용 여부, 동일한 도메인에서 로드되면 정상으로 간주
def check_favicon(url, response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')

        # 주소 표시줄의 도메인 추출
        base_domain = extract_domain(url)

        # 파비콘 URL 추출
        favicon_link = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        if favicon_link:
            favicon_url = favicon_link.get('href')
            # 파비콘 URL이 절대 경로인지 확인
            favicon_url = urljoin(url, favicon_url)
            parsed_favicon_url = urlparse(favicon_url)
            favicon_domain = parsed_favicon_url.netloc

            # 도메인 비교: .으로 분리한 후 첫 번째 문자열이 같은지 확인
            # 다른 도메인에서 로드된 경우 피싱으로 간주
            base_domain_first = base_domain.split('.')[0]
            favicon_domain_first = favicon_domain.split('.')[0]

            print(f"Base domain: {base_domain_first}")
            print(f"Favicon domain: {favicon_domain_first}")

            if base_domain_first == favicon_domain_first:
                return -1  # 첫 번째 문자열이 같으면 -1 반환
            else:
                return 1  # 첫 번째 문자열이 다르면 1 반환
        else:
            return 1  # 파비콘을 찾을 수 없는 경우 피싱

    except requests.RequestException as e:
        print(f"Favicon HTTP Exception Error: {e}")
        return 0
    except Exception as e:
        print(f"Favicon Exception Error: {e}")
        return 0 

# Request_URL
# 웹페이지 내의 외부 객체(이미지, 비디오, 소리 등)가 다른 도메인에서 로드되는지를 검사
def check_request_url(url, response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
            
        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')

        # 웹 페이지 도메인 추출
        website_domain = extract_domain(url)

        # 외부 객체(이미지, 비디오, 소리) 링크 추출
        imgs = soup.find_all('img', src=True)
        vids = soup.find_all('video', src=True)
        sounds = soup.find_all('audio', src=True)

        total = len(imgs) + len(vids) + len(sounds)
        linked_to_same = 0

        # 이미지 객체 도메인 검사
        for img in imgs:
            img_src = urljoin(url, img['src'])
            img_domain = extract_domain(img_src)
            if website_domain == img_domain or img_domain == '':
                linked_to_same += 1

        # 비디오 객체 도메인 검사
        for vid in vids:
            vid_src = urljoin(url, vid['src'])
            vid_domain = extract_domain(vid_src)
            if website_domain == vid_domain or vid_domain == '':
                linked_to_same += 1

        # 소리 객체 도메인 검사
        for sound in sounds:
            sound_src = urljoin(url, sound['src'])
            sound_domain = extract_domain(sound_src)
            if website_domain == sound_domain or sound_domain == '':
                linked_to_same += 1

        # 외부 링크 비율 계산
        linked_outside = total - linked_to_same
        avg = linked_outside / total if total != 0 else 0

        # 피싱 여부 판별
        threshold = 0.22  # 임계값 설정
        if avg > threshold:
            return 1  # 피싱으로 간주
        else:
            return -1  # 정상

    except requests.RequestException as e:
        print(f"Request_URL HTTP 요청 Error: {e}")
        return 0  
    except Exception as e:
        print(f"Request_URL Exception Error: {e}")
        return 0  

# URL_of_Anchor
# <a> 태그의 href 속성에 포함된 링크가 웹사이트의 도메인과 다른 도메인을 가리키는지 경우
def check_url_of_anchor(url, response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        
        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')
        
        # 웹 페이지 도메인 추출
        website_domain = extract_domain(url)

        # 앵커 태그 추출
        anchors = soup.find_all('a', href=True)
        external_links = 0
        invalid_links = 0

        for anchor in anchors:
            href = anchor['href']
            if href.startswith('http'):
                # 외부 도메인 링크 검사
                link_domain = extract_domain(href)
                if website_domain != link_domain:
                    external_links += 1
            elif href in ['#', 'javascript:']:
                # 유효하지 않은 링크 검사
                invalid_links += 1

        # 전체 앵커 태그 수
        total_anchors = len(anchors)
        
        if total_anchors == 0:
            return 0  # 앵커 태그가 없는 경우 의심하지 않음

        # 외부 링크 비율
        external_ratio = external_links / total_anchors
        invalid_ratio = invalid_links / total_anchors

        # 피싱 여부 판별
        if external_ratio > 0.5 or invalid_ratio > 0.5:
            return 1  # 피싱으로 간주
        elif external_ratio > 0.2 or invalid_ratio > 0.2:
            return 0  # 의심
        else:
            return -1  # 정상

    except requests.RequestException as e:
        print(f"URL_of_Anchor HTTP 요청 Error: {e}")
        return 0  
    except Exception as e:
        print(f"URL_of_Anchor Exception Error: {e}")
        return 0  

# Links_in_tags
# 합법적인 웹사이트에서는 HTML 문서에 대한 메타데이터를 제공하기 위해 
# <meta> 태그를 사용하는 것이 일반적
def has_meta_tags(response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        
        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')
        
        # <meta> 태그 찾기
        meta_tags = soup.find_all('meta')
        
        if meta_tags:
            return -1  # 메타 태그가 있으면 정상
        else:
            return 1  # 메타 태그가 없으면 피싱
        
    except requests.RequestException as e:
        print(f"Links_in_tags HTTP 요청 Error: {e}")
        return 1 
    except Exception as e:
        print(f"Links_in_tags Exception Error: {e}")
        return 0 

# SFH
# form 태그에서 action 속성(SFH)이 
# 빈 문자열, about:blank, 또는 웹페이지 도메인과 다른 도메인으로 설정되어 있는 경우를 검사
def check_sfh(url, response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        
        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')
        
        # 웹 페이지 도메인 추출
        website_domain = extract_domain(url)

        # SFH 확인
        forms = soup.find_all('form', action=True)
        for form in forms:
            action = form['action']
            if action in ['', 'about:blank']:
                return 1  # 빈 문자열이나 about:blank는 피싱으로 간주
            elif action.startswith('http'):
                action_domain = extract_domain(action)
                if website_domain != action_domain:
                    return 1  # 도메인이 다른 경우 피싱으로 간주
        
        return -1  # 모든 SFH가 정상인 경우

    except requests.RequestException as e:
        print(f"SFH HTTP 요청 Error: {e}")
        return 0  
    except Exception as e:
        print(f"SFH Exception Error: {e}")
        return 0 

# Submitting_to_email
# 피싱 공격자는 사용자의 정보를 자신의 개인 이메일로 리다이렉트할 수 있음
def check_submit_email(url, response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
            
        # 페이지 파싱
        soup = BeautifulSoup(response.content, 'lxml')
            
        # 서버 측 스크립트 함수와 mailto: 확인
        suspicious = False
        forms = soup.find_all('form', action=True)
        for form in forms:
            action = form['action']
            if 'mail(' in action or 'mailto:' in action:
                suspicious = True
                break
        # mail() 또는 mailto를 사용하면 피싱으로 간주
        return 1 if suspicious else -1
        
    except requests.RequestException as e:
        print(f"Submitting_to_email 요청 Error: {e}")
        return 0  
    except Exception as e:
        print(f"Submitting_to_email Exception Error: {e}")
        return 0 

# Redirect
# 피싱 웹사이트는 최소한 4번 이상 리디렉션된
def check_redirect_count(response):
    try:    
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
            
        # 리디렉션 횟수 확인
        redirect_count = len(response.history)
        
        if redirect_count >= 4:
            return 1  # 피싱 웹사이트로 간주
        elif 2 <= redirect_count < 4 :
            return 0 # 의심으로 간주
        else:
            return -1  # 합법적인 웹사이트로 간주
    
    except requests.RequestException as e:
        print(f"Redirect 요청 Error: {e}")
        return 0  
    except Exception as e:
        print(f"Redirect Exception Error: {e}")
        return 0

# on_mouseover
# 이벤트를 검사하여 상태 표시줄에서 변경이 이루어지는지를 확인
# 피싱 공격자는 JavaScript를 사용하여 상태 표시줄에 사용자에게 가짜 URL을 표시할 수 있음
def check_onmouseover_change(response):
    try:
        if response is None:
            raise requests.RequestException("Response is None")
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # 응답의 텍스트가 비어 있는 경우 피싱으로 간주
        if response.text.strip() == "":
            return 1 
            
        # onmouseover 이벤트 스크립트 검색:
        if re.search(r"<script.*?onmouseover.*?>", response.text, re.IGNORECASE):
            return 1 # onmouseover 이벤트를 포함하는 스크립트가 발견되면 피싱일 가능성
            
        return -1 

    except requests.RequestException as e:
        print(f"on_mouseover 요청 Error: {e}")
        return 0
    except Exception as e:
        print(f"on_mouseover Exception Error: {e}")
        return 0

    # try:
    #     # 웹 페이지 요청
    #     response = requests.get(url, timeout=5)
    #     response.raise_for_status()  # 요청이 실패하면 예외 발생
        
    #     # 페이지 파싱
    #     soup = BeautifulSoup(response.content, 'lxml')
        
    #     # onMouseOver 이벤트 검사
    #     scripts = soup.find_all('script')
    #     for script in scripts:
    #         if 'onMouseOver' in script.text:
    #             # 상태 표시줄 변경이 발견되면 피싱으로 간주
    #             if 'window.status' in script.text or 'window.defaultStatus' in script.text:
    #                 return 1 
        
    #     return -1  # 상태 표시줄 변경이 발견되지 않은 경우 정상으로 간주
        
    # except requests.RequestException as e:
    #     print(f"on_mouseover 요청 Error: {e}")
    #     return 0  
    # except Exception as e:
    #     print(f"on_mouseover Exception Error: {e}")
    #     return 0      
    

def classify_phishing(url):
    response = get_request_url(url)
    results = {
        "RightClick": use_right_click(response),
        "popUpWidnow": popup_window_text(response),
        "Iframe": iFrame_redirection(response),
        "having_IPhaving_IP_Address": using_ip(url),
        "Favicon": check_favicon(response),
        "Request_URL": check_request_url(response),
        "URL_of_Anchor": check_url_of_anchor(response),
        "Links_in_tags": has_meta_tags(response),
        "SFH": check_sfh(response),
        "Submitting_to_email": check_submit_email(response),
        "Redirect": check_redirect_count(response),
        "on_mouseover": check_onmouseover_change(response)
    }
    return results

def main():
    # URL과 상태를 포함한 딕셔너리
    test_urls = {
        "https://3u8kstpg-97iuu3sdu.vercel.app/": "피싱",
        "https://www.look.com.ua/": "정상",
        "https://viatraniver1972.blogspot.be": "피싱",
        "http://www.vogella.com/tutorials/JavaAlgorithmsDijkstra/article.html": "정상",
        "https://support-appleld.com.secureupdate.duilawyeryork.com/ap/ee636eeb7669742/?cmd=_update&dispatch=ee636eeb76697424b&locale=_": "피싱",
        "https://www.kia.com/cz/dealer/pemmbrno/": "정상",
        "http://kprealtors.com/ve/": "피싱",
        "http://www.ghbook.ir/index.php?lang=fa": "정상",
        "http://hello-d4cdd.firebaseapp.com/": "피싱",
        "https://www.eliteprospects.com/": "정상"
    }

    # 탐지 결과 출력
    for url, expected_status in test_urls.items():
        start_time = time.time()  # 시작 시간 기록
        
        results = classify_phishing(url)
        # 상태는 URL에 대한 예상 결과를 사용합니다
        status = expected_status

        print(f"Results for {url} (Status: {status}):")
        for key, value in results.items():
            result_status = "Phishing" if value == 1 else "Legitimate" if value == -1 else "Suspicious"
            print(f"{key}: {result_status}")

        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 실행 시간 계산
        print(f"컨텐츠 기반 피처 실행 시간: {elapsed_time:.4f} seconds")  # 실행 시간 출력
        print("-" * 40)

if __name__ == "__main__":
    main()