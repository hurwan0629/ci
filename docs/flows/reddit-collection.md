# Reddit 게시글 수집

현재 구현 범위는 서브레딧 하나에서 최신 게시글 한 페이지를 가져오는 함수입니다.
댓글 수집, 관련성 판단, 저장, 반복 실행, FastAPI 연결은 이후 작업입니다.

## 파일과 호출 계약

- `src/app/collectors/reddit.py`: `fetch_posts` 함수와 HTTP 요청 처리.
- `src/app/collectors/schema.py`: Pydantic 검증 모델. Reddit 전용 모델과 기타 플랫폼 모델을 주석 구간으로 구분합니다.
- `tests/unit/collectors/test_reddit.py`: 실제 네트워크를 사용하지 않는 단위 테스트.
- 두 폴더에 새 `__init__.py`는 추가하지 않았습니다. 기존 `src/app/__init__.py`는 유지합니다.

`fetch_posts(subreddit, *, client, limit=10)`은 `list[RedditPost]`를 반환합니다.

- `subreddit`: `python`처럼 이름만 전달합니다. 영문·숫자·밑줄을 허용하고 빈 값과 경로 문자는 거부합니다.
- `client`: OAuth Bearer 토큰과 식별 가능한 User-Agent가 설정된 `httpx.Client`. 생성과 종료는 호출자가 담당합니다.
- `limit`: 기본 10개이며 이번 구현의 범위는 정수 1~100입니다.
- 반환 필드: `id`, `title`, `body`, `url`. `url`은 외부 링크가 아닌 Reddit 게시글 원문 주소입니다.

## 흐름과 완료 조건

1. Pydantic으로 수집 입력을 검증합니다. 잘못된 입력으로는 HTTP 요청을 보내지 않습니다.
2. `GET https://oauth.reddit.com/r/{subreddit}/new`에 수집 개수를 전달합니다. 요청 타임아웃은 10초이며 리다이렉트는 따르지 않습니다.
3. HTTP 성공 여부와 응답 JSON의 목록·게시글 구조를 검증합니다.
4. 필요한 필드로 변환한 게시글을 요청 개수 이내로 반환합니다. 빈 목록은 `[]`로 반환합니다.

실패를 빈 결과로 바꾸지 않습니다. 입력·응답 검증 실패는 `pydantic.ValidationError`, HTTP 오류는 `httpx.HTTPStatusError`, 타임아웃은 해당 HTTPX 예외, 잘못된 JSON은 `json.JSONDecodeError`로 호출자에게 전달됩니다.
자동 재시도나 실패한 응답의 부분 반환은 하지 않습니다.

## 사용 예시

실제 호출에는 Reddit API 접근 권한과 유효한 OAuth 토큰이 필요합니다.
토큰 발급·갱신은 이번 함수의 범위에 포함되지 않습니다.
환경 변수에 인증 정보를 준비하고 `uv run python` 환경에서 다음과 같이 호출할 수 있습니다.

```python
import os

import httpx

from app.collectors.reddit import fetch_posts

with httpx.Client(
    headers={
        "Authorization": f"Bearer {os.environ['REDDIT_ACCESS_TOKEN']}",
        "User-Agent": os.environ["REDDIT_USER_AGENT"],
    }
) as client:
    posts = fetch_posts("python", client=client, limit=10)
    for post in posts:
        print(post.model_dump_json())
```

## 검증

```powershell
uv run pytest tests/unit/collectors/test_reddit.py
```

테스트는 HTTPX MockTransport의 가짜 응답으로 정상 매핑, 빈 목록, 개수 제한, 잘못된 입력, HTTP 오류, 타임아웃, 잘못된 목록·필드·JSON을 검증합니다.
실제 Reddit 접속, 계정 권한, 실제 응답과의 호환성은 아직 검증하지 않았습니다.

참고: [Reddit API](https://www.reddit.com/dev/api/), [인증 안내](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki), [HTTPX MockTransport](https://www.python-httpx.org/advanced/transports/#mock-transports).
