# CHANGELOG


## v0.0.0 (2026-09-05)

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
