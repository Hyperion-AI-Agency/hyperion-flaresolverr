# hyperion-flaresolverr

A `requests` transport adapter that transparently clears Cloudflare challenges
through a running [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
instance and reuses the harvested clearance for every later request to the same
host.

```python
import requests
from hyperion_flaresolverr import FlareSolverrAdapter

adapter = FlareSolverrAdapter(endpoint="http://localhost:8191/v1")
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

resp = session.get("https://a-cloudflare-protected-site.example")
print(resp.status_code, len(resp.text))

resp = session.get("https://a-cloudflare-protected-site.example/other")  # reuses clearance
print(resp.status_code, len(resp.text))

adapter.close()
```

Unchallenged requests pass straight through. When a challenge is detected the
adapter asks FlareSolverr to solve it once, keeps the cookies and user agent it
returns, and reuses them so FlareSolverr is touched once per host rather than
once per request. If a request is still challenged after retrying, the browser
HTML is returned instead of raising.

## Requires

A reachable FlareSolverr endpoint:

```
docker run -d --name flaresolverr -p 8191:8191 \
    ghcr.io/flaresolverr/flaresolverr:latest
```

## Install

```
pip install hyperion-flaresolverr
```

## Development

```
uv sync
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

On every commit, pre-commit runs Ruff (lint and format) and the test suite.
Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/)
and are checked by commitizen on the `commit-msg` hook.

```
uv run ruff check .
uv run ruff format .
uv run pytest -q
```

## Releasing

Releases are driven by [python-semantic-release](https://python-semantic-release.readthedocs.io/).
On every push to `main`, commit messages since the last release decide the next
version: `fix:` bumps patch, `feat:` bumps minor, a `!` or `BREAKING CHANGE:`
bumps major. It updates the version and `CHANGELOG.md`, tags `vX.Y.Z`, and cuts a
GitHub release. Commits with no releasable type publish nothing.

Publishing to PyPI uses [trusted publishing](https://docs.pypi.org/trusted-publishers/)
over OIDC, so no API token is stored in the repo. The trusted publisher must be
configured on PyPI (GitHub owner `hyperion-ai-agency`, repository
`hyperion-flaresolverr`, workflow `release.yml`) before the first release will
succeed.
