"""Fetch one page of recent Reddit posts using a caller-configured HTTP client."""

import httpx

from app.collectors.schema import RedditListing, RedditPost, RedditPostQuery


def fetch_posts(
    subreddit: str, *, client: httpx.Client, limit: int = 10
) -> list[RedditPost]:
    """Fetch recent posts; the caller supplies OAuth and User-Agent headers.

    Invalid inputs and response fields raise Pydantic ValidationError. HTTP,
    transport, and JSON decoding errors propagate to the caller without retrying.
    """
    query = RedditPostQuery.model_validate(
        {"subreddit": subreddit, "limit": limit}, strict=True
    )
    response = client.get(
        f"https://oauth.reddit.com/r/{query.subreddit}/new",
        params={"limit": query.limit},
        timeout=10.0,
        follow_redirects=False,
    )
    response.raise_for_status()
    listing = RedditListing.model_validate(response.json(), strict=True)
    return [post.data for post in listing.posts[: query.limit]]
