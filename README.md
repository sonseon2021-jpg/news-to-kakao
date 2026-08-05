# 동아일보 / 채널A 단독 뉴스 → 카카오톡 자동 전송

5분마다 네이버 뉴스에서 "동아일보 단독", "채널A 단독"을 검색해서,
새로 나온 기사만 카카오톡 "나에게 보내기"로 전송합니다.

## 준비 순서

1. **네이버 API 키 발급**
   - https://developers.naver.com → 애플리케이션 등록 → 사용 API에서 "검색" 체크
   - Client ID / Client Secret 확인

2. **카카오 API 키 발급 + 리프레시 토큰 발급**
   - https://developers.kakao.com → 앱 생성 → "카카오 로그인" 활성화
   - 동의항목에서 `talk_message` 사용 설정
   - 플랫폼 > Web에 Redirect URI로 `http://localhost:5000` 등록
   - `get_kakao_token.py` 의 `REST_API_KEY` 를 본인 앱 REST API 키로 수정 후 로컬에서 실행
     ```
     pip install requests
     python get_kakao_token.py
     ```
   - 안내에 따라 브라우저 인증 → code 값 입력 → `refresh_token` 확보

3. **이 폴더를 GitHub 저장소로 업로드**
   - 새 저장소 생성 후 이 폴더의 내용을 그대로 push

4. **GitHub Secrets 등록**
   저장소 > Settings > Secrets and variables > Actions > New repository secret 에서 아래 4개 등록:
   - `NAVER_CLIENT_ID`
   - `NAVER_CLIENT_SECRET`
   - `KAKAO_REST_API_KEY`
   - `KAKAO_REFRESH_TOKEN`

5. **워크플로우 활성화 확인**
   - 저장소 Actions 탭에서 "단독 뉴스 카톡 전송" 워크플로우가 보이는지 확인
   - 처음엔 "Run workflow" 버튼으로 수동 실행해서 정상 작동하는지 테스트 권장
   - 이후엔 5분마다 자동 실행됨

## 참고 사항

- 카카오 Access Token은 6시간마다 만료되지만, 스크립트가 매번 Refresh Token으로
  새 Access Token을 발급받아 쓰므로 별도 조치가 필요 없습니다.
- 단, **Refresh Token 자체는 카카오 로그인을 6개월 이상 하지 않으면 만료**됩니다.
  워크플로우가 5분마다 계속 실행되는 한 문제 없습니다.
- 처음 실행 시 과거 기사가 몰려서 전송되는 걸 막고 싶다면, 최초 1회는 로컬에서
  `main.py`를 실행해 `sent_links.json`을 미리 채워둔 뒤 커밋하세요.
- 채널A의 정확한 도메인은 실제 검색 결과를 보고 `main.py`의 `SOURCE_DOMAINS`를
  조정하시는 걸 추천합니다.
