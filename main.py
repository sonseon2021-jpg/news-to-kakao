"""
'동아일보' 또는 '채널A'라는 단어가 들어간 뉴스를(어느 언론사 기사든) 네이버 뉴스 검색에서
찾아 카카오톡(나에게 보내기)으로 전달하는 스크립트.

필요한 환경변수 (GitHub Secrets에 등록):
- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET
- KAKAO_REST_API_KEY
- KAKAO_CLIENT_SECRET
- KAKAO_REFRESH_TOKEN
"""

import os
import re
import json
import requests

NAVER_CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]
KAKAO_REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
KAKAO_CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
KAKAO_REFRESH_TOKEN = os.environ["KAKAO_REFRESH_TOKEN"]

SENT_LINKS_FILE = "sent_links.json"
MAX_STORED_LINKS = 500  # 파일이 무한정 커지지 않도록 최근 N개만 보관

SEARCH_QUERIES = ["동아일보", "채널A"]

# 이 도메인에서 나온 기사는 '동아일보/채널A 본인이 쓴 기사'이므로 제외합니다.
EXCLUDE_DOMAINS = ["donga.com", "ichannela.com", "dongascience.com"]


def clean_title(raw_title: str) -> str:
    return re.sub(r"</?b>", "", raw_title).replace("&quot;", '"').replace("&amp;", "&")


def search_naver_news(query: str):
    url = "https://naverapihub.apigw.ntruss.com/search/v1/news"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 20, "sort": "date", "format": "json"}
    res = requests.get(url, headers=headers, params=params, timeout=10)
    res.raise_for_status()
    return res.json().get("items", [])


def is_other_outlet_article(item: dict) -> bool:
    link = item.get("originallink", "") + item.get("link", "")
    return not any(domain in link for domain in EXCLUDE_DOMAINS)


def load_sent_links() -> set:
    if not os.path.exists(SENT_LINKS_FILE):
        return set()
    with open(SENT_LINKS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_sent_links(links: set):
    trimmed = list(links)[-MAX_STORED_LINKS:]
    with open(SENT_LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def get_kakao_access_token() -> str:
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "client_secret": KAKAO_CLIENT_SECRET,
        "refresh_token": KAKAO_REFRESH_TOKEN,
    }
    res = requests.post(url, data=data, timeout=10)
    res.raise_for_status()
    return res.json()["access_token"]


def send_kakao_message(access_token: str, title: str, link: str):
    # 링크를 별도 버튼(link 필드)이 아니라 본문 텍스트에 그대로 포함시켜서,
    # 카카오의 '웹 도메인 등록' 제한 없이도 자동으로 눌러서 이동 가능하게 합니다.
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    template = {
        "object_type": "text",
        "text": f"{title}\n{link}",
    }
    data = {"template_object": json.dumps(template, ensure_ascii=False)}
    res = requests.post(url, headers=headers, data=data, timeout=10)
    if res.status_code != 200:
        print("카카오 응답 코드:", res.status_code)
        print("카카오 응답 내용:", res.text)
    res.raise_for_status()


def main():
    sent_links = load_sent_links()
    new_articles = []

    for query in SEARCH_QUERIES:
        for item in search_naver_news(query):
            link = item.get("originallink") or item.get("link")
            if link in sent_links:
                continue
            if is_other_outlet_article(item):
                new_articles.append(item)
                sent_links.add(link)

    if not new_articles:
        print("새로운 기사 없음.")
        return

    access_token = get_kakao_access_token()
    for item in new_articles:
        title = clean_title(item["title"])
        link = item.get("originallink") or item.get("link")
        send_kakao_message(access_token, title, link)
        print("전송 완료:", title)

    save_sent_links(sent_links)


if __name__ == "__main__":
    main()
