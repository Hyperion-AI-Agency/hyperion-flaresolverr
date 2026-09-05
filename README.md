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

## Releasing

Publishing uses PyPI [trusted publishing](https://docs.pypi.org/trusted-publishers/)
over OIDC, so no API token is stored in the repo. The trusted publisher must be
configured on PyPI (GitHub owner `hyperion-ai-agency`, repository
`hyperion-flaresolverr`, workflow `release.yml`) before the first tagged release
will succeed. Then push a tag matching `v*` to build and publish.
