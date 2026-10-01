#!/bin/bash
# Installeert Agent Reach (internettoegang voor Claude) in cloudsessies.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Vastgezet op een geteste versie; verhoog bewust bij updates.
AGENT_REACH_REF="a19a171fa980a0785849596492e0af4db800c82f"
VENV="$HOME/.agent-reach-venv"

if [ ! -x "$VENV/bin/agent-reach" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --disable-pip-version-check "git+https://github.com/Panniantong/agent-reach@${AGENT_REACH_REF}"
fi

export PATH="$VENV/bin:$PATH"
echo "export PATH=\"$VENV/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"

# Alleen kanalen zonder login/cookies: web, zoeken (Exa), YouTube, GitHub, RSS.
if ! command -v mcporter >/dev/null 2>&1 || [ ! -f "$HOME/.claude/skills/agent-reach/SKILL.md" ]; then
  agent-reach install --env=auto --system >/dev/null
fi
