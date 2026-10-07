#!/usr/bin/env bash
# Start the free-token LLM router for the engine and load your provider keys into it.
#   bash scripts/router_setup.sh        # OmniRoute on http://localhost:20128/v1 (model "auto")
#   python scripts/llm.py --check       # then: what works, and how many free tokens a month are live
# Needs outbound network to the providers (cloud environment: Network access = Full). Keys come from
# environment variables (docs/llm-router.md); they are piped to OmniRoute on stdin and never printed or saved here.
set -uo pipefail
if ! curl -s -m 3 http://localhost:20128/v1/models >/dev/null 2>&1; then
  command -v omniroute >/dev/null 2>&1 || npm install -g omniroute >/tmp/omniroute-install.log 2>&1
  nohup omniroute > /tmp/omniroute.log 2>&1 &
  for i in $(seq 1 60); do curl -s -m 2 http://localhost:20128/v1/models >/dev/null 2>&1 && break; sleep 2; done
fi
# providers OmniRoute's CLI can register (the rest are called directly by scripts/llm.py)
for pair in mistral:MISTRAL_API_KEY groq:GROQ_API_KEY openrouter:OPENROUTER_API_KEY; do
  prov=${pair%%:*}; var=${pair#*:}
  if [ -n "${!var:-}" ]; then
    printf '%s' "${!var}" | omniroute keys add "$prov" --stdin >/dev/null 2>&1 && echo "OmniRoute: $prov key loaded" || echo "OmniRoute: $prov key not loaded"
  fi
done
curl -s -m 5 http://localhost:20128/v1/models >/dev/null && echo "OmniRoute up on http://localhost:20128/v1"
