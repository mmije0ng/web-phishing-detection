import requests
import whois
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Google Safe Browsing API 키
API_KEY = 'AIzaSyD2OaMfUyIk8Zq0BOJs_hCoM_WRZEInx1g'
API_URL = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}'

# 위협 유형 리스트
THREAT_TYPES = [
    "MALWARE",
    "SOCIAL_ENGINEERING",
    "UNWANTED_SOFTWARE",
    "POTENTIALLY_HARMFUL_APPLICATION"
]

# Helper Functions
def google_index(url):
    try:
        response = requests.get(f"https://www.google.com/search?q=site:{urlparse(url).netloc}")
        return 1 if 'No results' not in response.text else 0
    except requests.RequestException:
        return -1

def domain_age(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return -1
        age_days = (datetime.datetime.now() - creation_date).days
        if age_days >= 3031:
            return 0
        else:
            return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1

def dns_record(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        if domain_info is None or domain_info.status is None:
            return 1
        return 0
    except Exception as e:
        print(f"Whois 조회 중 오류 발생: {e}")
        return -1

def domain_registration_period(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        if domain_info.creation_date is None:
            return -1
        if isinstance(domain_info.creation_date, list):
            creation_date = domain_info.creation_date[0]
        else:
            creation_date = domain_info.creation_date
        if isinstance(creation_date, datetime.datetime):
            age_days = (datetime.datetime.now() - creation_date).days
        else:
            return -1
        if age_days < 180:
            return 1
        else:
            return 0
    except Exception as e:
        print(f"Whois 조회 중 오류 발생: {e}")
        return -1

def ssl_certificate_status(url):
    try:
        response = requests.get(url, timeout=5)
        return 0 if 'https' in response.url else 1
    except requests.RequestException:
        return 1

def safe_browsing(url):
    body = {
        'client': {
            'clientId': 'yourcompany',
            'clientVersion': '1.0.0'
        },
        'threatInfo': {
            'threatTypes': THREAT_TYPES,
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [{'url': url}]
        }
    }
    try:
        response = requests.post(API_URL, json=body)
        if response.status_code == 200:
            result = response.json()
            return 1 if result.get('matches') else 0
        else:
            return -1
    except requests.RequestException:
        return -1

def having_sub_domain(url):
    return 1 if len(urlparse(url).path.split('.')) > 2 else 0

def https_token(url):
    return 1 if 'https' in urlparse(url).netloc else 0

def web_traffic(url):
    # Note: Web traffic data typically requires specialized APIs or services.
    # This is a placeholder implementation.
    return -1  # Placeholder for actual traffic data lookup

def page_rank(url):
    # Note: Google PageRank API is not publicly available.
    # This is a placeholder implementation.
    return -1  # Placeholder for actual PageRank lookup

def links_pointing_to_page(url):
    # Placeholder implementation, actual implementation would require crawling the web.
    return -1  # Placeholder for actual link count lookup

def statistical_report(url):
    # Placeholder for checking against PhishTank or StopBadware databases.
    return -1  # Placeholder for actual statistical report lookup

def main():
    test_urls = [
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
        "https://www.astrologyonline.eu/Astro_MemoNew/Profilo.asp",
        "https://www.lifewire.com/tcp-port-21-818146",
        "https://technofizi.net/top-best-mp3-downloader-app-for-android-free-music-download/",
        "http://html.house/l7ceeid6.html",
        "https://www.missfiga.com/",
        "http://wave.progressfilm.co.uk/time3/?logon=myposte",
        "https://www.chiefarchitect.com/",
        "http://beta.kenaidanceta.com/postamok/d39a2/source",
        "http://www.ktplasmachinery.com/cs/",
        "http://www.2345daohang.com/",
        "http://www.game.co.uk/en/games/nintendo-switch/nintendo-switch/",
        "https://blog.hubspot.com/marketing/email-open-click-rate-benchmark",
        "http://batvrms.net/deliver/D2017HL/u.php",
        "http://sophie-world.com/games/port-and-starboard",
        "http://support-appleld.com.secureupdate.duilawyeryork.com/ap/bb14d7ff1fcbf29?cmd=_update&dispatch=bb14d7ff1fcbf29bb&locale=_"
    ]

    for url in test_urls:
        print(f"URL: {url}")
        print(f"Google Index: {google_index(url)}")
        print(f"Domain Age: {domain_age(url)}")
        print(f"DNS Record: {dns_record(url)}")
        print(f"Domain Registration Period: {domain_registration_period(url)}")
        print(f"SSL Certificate Status: {ssl_certificate_status(url)}")
        print(f"Safe Browsing: {safe_browsing(url)}")
        print(f"Having Sub Domain: {having_sub_domain(url)}")
        print(f"HTTPS Token: {https_token(url)}")
        print(f"Web Traffic: {web_traffic(url)}")
        print(f"Page Rank: {page_rank(url)}")
        print(f"Links Pointing to Page: {links_pointing_to_page(url)}")
        print(f"Statistical Report: {statistical_report(url)}")
        print("-" * 50)

if __name__ == "__main__":
    main()
