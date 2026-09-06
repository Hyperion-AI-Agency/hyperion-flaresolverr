# CHANGELOG


## v0.2.0 (2026-09-06)

### Chores

- Add Copier setup to vendor the module + tests into projects
  ([#8](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/8),
  [`945af35`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/945af354fefca5ef4f9de121de5d21eceb367a64))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

### Features

- Vendor the library into projects via Copier
  ([#9](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/9),
  [`722de77`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/722de771f6f31961980bcb24603dfdea50dd791f))

Explicit answers file + version-pin docs, and ship copier.yml in a release tag so 'copier copy
  gh:...' resolves the vendor config by default.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

### Refactoring

- Move FlareSolverrError into an exceptions subpackage
  ([#6](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/6),
  [`81ecc37`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/81ecc3719e1ee60f1058654eb68e225429e78643))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

- Put FlareSolverrError in exceptions/errors.py, not the package init
  ([#7](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/7),
  [`6bfbfba`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/6bfbfba1ec3368f56bce1880a3f46019346f30cb))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt


## v0.1.1 (2026-09-05)

### Bug Fixes

- Detect Cloudflare block pages whose marker is past the first 4KB
  ([#5](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/5),
  [`6435973`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/6435973c9c82e4060e2521a951c04f07734ca822))

The 'Attention Required! | Cloudflare' 403 page carries its challenge-platform marker ~4.8KB in,
  past the old 4000-char scan window, so it slipped through undetected and the 403 was returned
  as-is. Widen the scan to 20000 chars and add the 'attention required' marker. Verified live
  against oddschecker: challenge is now solved and the real page returned.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

### Chores

- Restore version to 0.1.0 and set v0.1.0 as release baseline
  ([#3](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/3),
  [`83c3ea9`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/83c3ea90162892b6942b044bbfee86cb4543a84e))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

- Space out adapter and run tests in pre-commit
  ([#4](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/4),
  [`917267a`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/917267a7837225d07fde813642716dce1af9d7dc))

Add blank lines between logical blocks in adapter.py (magic trailing commas keep calls expanded
  under ruff format). Add a pytest hook so pre-commit lints, formats, and tests.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt


## v0.1.0 (2026-09-05)

### Chores

- Add ruff format, pre-commit, commit linting, and semantic-release
  ([#1](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/1),
  [`275d689`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/275d68938fcca42a69bddef944499abb29b0e658))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt

### Continuous Integration

- Build distributions on the runner, not in the semantic-release container
  ([#2](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/pull/2),
  [`d839bd3`](https://github.com/Hyperion-AI-Agency/hyperion-flaresolverr/commit/d839bd308df7bdc4a2a75f7adf09a86fb71c9f9c))

python-semantic-release runs in its own Docker image without uv, so build_command 'uv build' exited
  127. PSR now only versions/tags/changelogs; build + publish run as runner steps where uv exists.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01PBsRau1b69sNDJwtaCSVrt
