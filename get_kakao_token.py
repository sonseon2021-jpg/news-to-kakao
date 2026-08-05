"""
카카오 '나에게 보내기' 기능을 쓰기 위한 Refresh Token을 최초 1회 발급받는 스크립트.

사용법:
1. https://developers.kakao.com 에서 앱을 만들고,
   - "카카오 로그인" 활성화
   - "동의항목"에서 talk_message 를 사용 설정
   - "플랫폼"에 Redirect URI로 http://localhost:5000 등록
2. 아래 REST_API_KEY 를 본인의 앱 REST API 키로 바꾸고 이 스크립트를 실행
3. 안내되는 URL을 브라우저에 붙여넣어 로그인/동의
4. 리다이렉트된 주소창의 code= 뒤 값을 복사해서 입력
5. 출력된 refresh_token 을 GitHub 저장소 Secrets에 KAKAO_REFRESH_TOKEN 으로 등록
"""

import requests

REST_API_KEY = "여기에_본인의_카카오_REST_API_키"
REDIRECT_URI = "http://localhost:5000"


def main():
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope=talk_message"
    )
    print("아래 URL을 브라우저에 열고 로그인/동의 후,")
    print("리다이렉트된 주소창에서 code=... 부분의 값을 복사하세요.\n")
    print(auth_url, "\n")

    code = input("복사한 code 값을 붙여넣으세요: ").strip()

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    res = requests.post(token_url, data=data)
    res.raise_for_status()
    tokens = res.json()

    print("\n=== 발급 완료 ===")
    print("access_token :", tokens["access_token"])
    print("refresh_token:", tokens["refresh_token"])
    print("\n이 중 refresh_token 값을 GitHub 저장소의")
    print("Settings > Secrets and variables > Actions 에")
    print("이름 KAKAO_REFRESH_TOKEN 으로 등록하세요.")


if __name__ == "__main__":
    main()
