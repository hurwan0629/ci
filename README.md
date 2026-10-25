# Community Collector

사용자가 만든 섹션의 상황과 수집 조건에 맞는 게시글 및 관련 댓글을 모아보는 서비스입니다.
프로젝트 이름은 임시 이름이며, 현재는 Reddit의 최신 게시글을 가져오는 수집 함수까지 구현되어 있습니다.

## 시작하기

Python 3.12와 [uv](https://docs.astral.sh/uv/)를 사용합니다.

```powershell
uv sync --locked
```

아직 실행 가능한 웹 서버는 없습니다. Reddit 수집 함수의 사용법과 검증 범위는 [Reddit 수집 문서](docs/flows/reddit-collection.md)를 참고합니다.
DB를 도입할 때는 Docker 기반 PostgreSQL과 마이그레이션을 사용합니다.

## 검증

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

TDD는 동작의 완료 조건 정의 → 실패하는 테스트 → 최소 구현 → 리팩터링 순서로 진행합니다.
패키지 import와 Reddit 수집 함수의 동작을 검증합니다. HTTP 요청은 MockTransport로 대체하므로 테스트와 CI에 Reddit 접속이나 인증 정보가 필요하지 않습니다.

Reddit 수집 테스트만 실행하려면 다음 명령을 사용합니다.

```powershell
uv run pytest tests/unit/collectors/test_reddit.py
```

## 구조

- `src/app/`: 애플리케이션 코드. 세부 모듈은 기능을 구현하면서 나눕니다.
- `src/app/collectors/reddit.py`: Reddit 최신 게시글 수집 함수.
- `src/app/collectors/schema.py`: 플랫폼별 수집 입력·응답 검증 모델. 주석으로 플랫폼 구간을 구분합니다.
- `tests/unit/`: 독립적인 동작의 테스트.
- `tests/integration/`: DB 및 외부 서비스 연동 경계의 테스트.
- `docs/`: 제품 정의, 작업 목록, 사용자 흐름, 기술 결정, HTML 시안.
- `.github/workflows/ci.yml`: 테스트, 린트, 포맷, 타입 검사.

문서의 시작점은 [docs/index.md](docs/index.md), 작업 규칙은 [AGENTS.md](AGENTS.md)입니다.
