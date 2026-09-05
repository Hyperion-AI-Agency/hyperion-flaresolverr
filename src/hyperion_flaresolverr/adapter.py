import logging
import threading
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from requests.structures import CaseInsensitiveDict

log = logging.getLogger(__name__)

CHALLENGE_STATUSES = {403, 429, 503}
CHALLENGE_MARKERS = (
    "just a moment",
    "cf-browser-verification",
    "challenge-platform",
    "_cf_chl_opt",
    "enable javascript and cookies to continue",
)


class FlareSolverrError(RuntimeError):
    pass


class FlareSolverrAdapter(HTTPAdapter):
    def __init__(
        self,
        endpoint="http://localhost:8191/v1",
        session_id="requests-adapter",
        max_timeout=60000,
        upstream_proxy=None,
        always=False,
        **kwargs,
    ):
        self.endpoint = endpoint
        self.session_id = session_id
        self.max_timeout = max_timeout
        self.upstream_proxy = upstream_proxy
        self.always = always
        self._lock = threading.Lock()
        self._creds = {}
        self._session_ready = False
        # A plain session for talking to FlareSolverr itself. It must not have
        # this adapter mounted on it or the first challenge recurses forever.
        self._rpc = requests.Session()
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        host = urlparse(request.url).netloc
        self._apply_creds(request, host)
        if self.always:
            return self._build_response(request, self._solve(request.url))
        response = super().send(request, **kwargs)
        if not self._is_challenge(response):
            return response
        log.info("challenge on %s, handing to flaresolverr", host)
        solution = self._solve(request.url)
        self._store_creds(host, solution)
        retry = request.copy()
        self._apply_creds(retry, host)
        response.close()
        retried = super().send(retry, **kwargs)
        if not self._is_challenge(retried):
            return retried
        log.warning("still challenged after clearance, returning browser html")
        retried.close()
        return self._build_response(request, solution)

    def close(self):
        if self._session_ready:
            try:
                self._call({"cmd": "sessions.destroy", "session": self.session_id})
            except Exception:
                log.debug("could not destroy flaresolverr session", exc_info=True)
            self._session_ready = False
        self._rpc.close()
        super().close()

    def _is_challenge(self, response):
        if response.status_code not in CHALLENGE_STATUSES:
            return False
        # Cloudflare sets this on anything it blocked or challenged itself,
        # which distinguishes its 403 from the origin's own 403.
        if "cf-mitigated" in response.headers:
            return True
        if "cloudflare" not in response.headers.get("server", "").lower():
            return False
        try:
            body = response.text[:4000].lower()
        except Exception:
            return False
        return any(marker in body for marker in CHALLENGE_MARKERS)

    def _call(self, payload):
        reply = self._rpc.post(self.endpoint, json=payload, timeout=(self.max_timeout / 1000) + 15)
        reply.raise_for_status()
        data = reply.json()
        if data.get("status") != "ok":
            raise FlareSolverrError(data.get("message") or "flaresolverr returned an error")
        return data

    def _ensure_session(self):
        with self._lock:
            if self._session_ready:
                return
            payload = {"cmd": "sessions.create", "session": self.session_id}
            if self.upstream_proxy:
                payload["proxy"] = {"url": self.upstream_proxy}
            try:
                self._call(payload)
            except FlareSolverrError as exc:
                if "exists" not in str(exc).lower():
                    raise
            self._session_ready = True

    def _solve(self, url):
        self._ensure_session()
        return self._call(
            {
                "cmd": "request.get",
                "url": url,
                "maxTimeout": self.max_timeout,
                "session": self.session_id,
            }
        )["solution"]

    def _store_creds(self, host, solution):
        self._creds[host] = {
            "cookies": {c["name"]: c["value"] for c in solution.get("cookies", [])},
            "user_agent": solution.get("userAgent"),
        }

    def _apply_creds(self, request, host):
        creds = self._creds.get(host)
        if not creds:
            return
        # cf_clearance is bound to the user agent that earned it. Send one
        # without the other and Cloudflare challenges you again.
        if creds["user_agent"]:
            request.headers["User-Agent"] = creds["user_agent"]
        existing = request.headers.get("Cookie")
        jar = {}
        if existing:
            for pair in existing.split("; "):
                if "=" in pair:
                    name, value = pair.split("=", 1)
                    jar[name] = value
        jar.update(creds["cookies"])
        request.headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in jar.items())

    def _build_response(self, request, solution):
        response = Response()
        response.status_code = solution.get("status", 200)
        response.headers = CaseInsensitiveDict(solution.get("headers") or {})
        # The body is what the browser rendered, already decoded. Leaving these
        # headers in place makes requests try to gunzip plain text.
        response.headers.pop("content-encoding", None)
        response.headers.pop("content-length", None)
        response._content = (solution.get("response") or "").encode("utf-8")
        response.encoding = "utf-8"
        response.url = solution.get("url", request.url)
        response.reason = "OK"
        response.request = request
        return response
