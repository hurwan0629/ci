# Community Collector

사용자가 만든 섹션의 상황과 수집 조건에 맞는 게시글 및 관련 댓글을 모아보는 서비스입니다.
프로젝트 이름은 임시 이름이며, 현재는 개발 환경과 문서 구조만 준비되어 있습니다.

## 시작하기

Python 3.12와 [uv](https://docs.astral.sh/uv/)를 사용합니다.

```powershell
uv sync --locked
```

아직 실행 가능한 웹 서버나 수집 기능은 없습니다. DB를 도입할 때는 Docker 기반 PostgreSQL과 마이그레이션을 사용합니다.

## 검증

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

TDD는 동작의 완료 조건 정의 → 실패하는 테스트 → 최소 구현 → 리팩터링 순서로 진행합니다.
현재 테스트는 패키지 import를 확인하는 환경 점검용입니다.

## 구조

- `src/app/`: 애플리케이션 코드. 세부 모듈은 기능을 구현하면서 나눕니다.
- `tests/unit/`: 독립적인 동작의 테스트.
- `tests/integration/`: DB 및 외부 서비스 연동 경계의 테스트.
- `docs/`: 제품 정의, 작업 목록, 사용자 흐름, 기술 결정, HTML 시안.
- `.github/workflows/ci.yml`: 테스트, 린트, 포맷, 타입 검사.

문서의 시작점은 [docs/index.md](docs/index.md), 작업 규칙은 [AGENTS.md](AGENTS.md)입니다.
