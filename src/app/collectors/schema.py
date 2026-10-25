"""수집기의 외부 입력과 응답을 검증하는 Pydantic 스키마."""

from pydantic import AliasPath, BaseModel, Field, HttpUrl, field_validator

# ---------------------------------------------------------------------------
# Reddit 전용 스키마
# ---------------------------------------------------------------------------


class RedditPost(BaseModel):
    """Reddit 게시글의 필드를 검증하고 토론 원문 주소를 구성한다."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str = Field(validation_alias="selftext")
    url: HttpUrl = Field(validation_alias="permalink")

    @field_validator("url", mode="before")
    @classmethod
    def build_post_url(cls, value: object) -> str:
        if not isinstance(value, str) or not value.startswith("/r/"):
            raise ValueError("Expected a Reddit-relative post permalink")
        return f"https://www.reddit.com{value}"


class RedditPostQuery(BaseModel):
    """조회할 서브레딧 이름과 게시글 개수를 검증한다."""

    subreddit: str = Field(pattern=r"^[A-Za-z0-9_]+$")
    limit: int = Field(ge=1, le=100)


class RedditListingPost(BaseModel):
    """Reddit 목록 응답의 개별 게시글 항목을 검증한다."""

    data: RedditPost


class RedditListing(BaseModel):
    """Reddit 목록 응답에서 게시글 항목들을 추출하고 검증한다."""

    posts: list[RedditListingPost] = Field(
        validation_alias=AliasPath("data", "children")
    )


# ---------------------------------------------------------------------------
# 기타 플랫폼 스키마 (플랫폼 추가 시 아래에 정의)
# ---------------------------------------------------------------------------
