from json import JSONDecodeError, dumps

import httpx
import pytest
from pydantic import ValidationError

from app.collectors.reddit import fetch_posts


@pytest.fixture
def post_data() -> dict[str, object]:
    """테스트에서 사용할 Reddit 게시글 원본 데이터를 제공한다."""
    return {
        "id": "abc123",
        "title": "A useful Python discussion",
        "selftext": "Some practical experience.",
        "permalink": "/r/python/comments/abc123/a_useful_python_discussion/",
        "url": "https://example.com/linked-article",
    }


def _listing(*posts: dict[str, object]) -> dict[str, object]:
    """게시글들을 Reddit API의 목록 응답 구조로 감싼다."""
    return {"data": {"children": [{"kind": "t3", "data": post} for post in posts]}}


def _client(response: httpx.Response) -> httpx.Client:
    """실제 통신 없이 지정한 응답을 반환하는 HTTP 클라이언트를 만든다."""
    return httpx.Client(transport=httpx.MockTransport(lambda request: response))


def test_fetch_posts_requests_latest_posts_and_maps_fields(
    post_data: dict[str, object],
) -> None:
    """최신 글 요청 설정과 게시글 필드·원문 URL 변환이 올바른지 확인한다."""

    def handler(request: httpx.Request) -> httpx.Response:
        """요청 경로·개수·헤더·타임아웃을 검사하고 정상 목록을 반환한다."""
        assert request.method == "GET"
        assert request.url.host == "oauth.reddit.com"
        assert request.url.path == "/r/python/new"
        assert request.url.params["limit"] == "2"
        assert request.headers["Authorization"] == "Bearer test-token"
        assert request.headers["User-Agent"] == "community-collector-test"
        assert request.extensions["timeout"]["read"] == 10.0
        return httpx.Response(200, json=_listing(post_data))

    with httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={
            "Authorization": "Bearer test-token",
            "User-Agent": "community-collector-test",
        },
    ) as client:
        posts = fetch_posts("python", client=client, limit=2)

    assert [post.model_dump(mode="json") for post in posts] == [
        {
            "id": "abc123",
            "title": "A useful Python discussion",
            "body": "Some practical experience.",
            "url": "https://www.reddit.com/r/python/comments/abc123/a_useful_python_discussion/",
        }
    ]


def test_fetch_posts_returns_empty_list_when_no_posts_exist() -> None:
    """수집된 게시글이 없으면 빈 목록을 반환하는지 확인한다."""
    with _client(httpx.Response(200, json=_listing())) as client:
        assert fetch_posts("python", client=client) == []


def test_fetch_posts_respects_requested_limit(post_data: dict[str, object]) -> None:
    """응답에 게시글이 더 많아도 요청한 개수까지만 반환하는지 확인한다."""
    with _client(httpx.Response(200, json=_listing(post_data, post_data))) as client:
        assert len(fetch_posts("python", client=client, limit=1)) == 1


@pytest.mark.parametrize(
    ("subreddit", "limit"),
    [("", 10), ("r/python", 10), ("../python", 10), ("python", 0), ("python", 101)],
)
def test_fetch_posts_rejects_invalid_input_before_request(
    subreddit: str, limit: int
) -> None:
    """잘못된 서브레딧 이름과 수집 개수를 HTTP 요청 전에 거부하는지 확인한다."""

    def handler(request: httpx.Request) -> httpx.Response:
        """입력 검증에 실패했는데 HTTP 요청까지 실행되면 테스트를 실패시킨다."""
        pytest.fail("Invalid input must not make an HTTP request")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValidationError):
            fetch_posts(subreddit, client=client, limit=limit)


@pytest.mark.parametrize("status_code", [401, 403, 429, 500])
def test_fetch_posts_propagates_http_errors(status_code: int) -> None:
    """인증·권한·요청 제한·서버 오류의 상태 코드가 HTTP 예외로 전달되는지 확인한다."""
    with _client(httpx.Response(status_code)) as client:
        with pytest.raises(httpx.HTTPStatusError) as error:
            fetch_posts("python", client=client)

    assert error.value.response.status_code == status_code


def test_fetch_posts_propagates_timeouts() -> None:
    """응답 대기 중 발생한 타임아웃이 호출자에게 전달되는지 확인한다."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Reddit 응답을 기다리다 읽기 타임아웃이 발생한 상황을 재현한다."""
        raise httpx.ReadTimeout("Reddit timed out", request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.ReadTimeout):
            fetch_posts("python", client=client)


@pytest.mark.parametrize("payload", [None, {}, {"data": {"children": {}}}])
def test_fetch_posts_rejects_malformed_listings(payload: object) -> None:
    """JSON 값이 Reddit 목록 응답 구조와 다르면 검증 오류가 발생하는지 확인한다."""
    with _client(httpx.Response(200, content=dumps(payload))) as client:
        with pytest.raises(ValidationError):
            fetch_posts("python", client=client)


@pytest.mark.parametrize(
    ("field", "value"),
    [("id", 123), ("title", ""), ("permalink", "https://example.com/post")],
)
def test_fetch_posts_rejects_invalid_post_fields(
    post_data: dict[str, object], field: str, value: object
) -> None:
    """게시글 ID·제목·원문 경로가 잘못되면 검증 오류가 발생하는지 확인한다."""
    post_data[field] = value
    with _client(httpx.Response(200, json=_listing(post_data))) as client:
        with pytest.raises(ValidationError):
            fetch_posts("python", client=client)


def test_fetch_posts_rejects_invalid_json() -> None:
    """응답 본문이 JSON이 아니면 JSON 해석 오류가 전달되는지 확인한다."""
    with _client(httpx.Response(200, text="not JSON")) as client:
        with pytest.raises(JSONDecodeError):
            fetch_posts("python", client=client)
