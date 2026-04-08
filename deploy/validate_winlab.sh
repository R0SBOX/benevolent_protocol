#!/usr/bin/env bash
set -euo pipefail

WINLAB_HOST="${WINLAB_HOST:-192.168.122.248}"
WINLAB_USER="${WINLAB_USER:-John}"
WINLAB_KEY="${WINLAB_KEY:-$HOME/.ssh/id_ed25519}"
WINLAB_KNOWN_HOSTS="${WINLAB_KNOWN_HOSTS:-/tmp/benevolent_known_hosts}"
WINLAB_REPO_PATH="${WINLAB_REPO_PATH:-C:\\Users\\John\\benevolent_protocol}"

ssh_base=(
  ssh
  -i "$WINLAB_KEY"
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile="$WINLAB_KNOWN_HOSTS"
  "${WINLAB_USER}@${WINLAB_HOST}"
)

echo "[1/4] Ensuring Python 3.12 is available on the VM..."
if ! "${ssh_base[@]}" "cmd /c py -3.12 --version" >/dev/null 2>&1; then
  "${ssh_base[@]}" "cmd /c winget install -e --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements --disable-interactivity"
fi

echo "[2/4] Ensuring virtualenv and dependencies are ready..."
"${ssh_base[@]}" \
  "powershell -NoProfile -Command \"Set-Location '${WINLAB_REPO_PATH}'; if (-not (Test-Path .venv\\Scripts\\python.exe)) { py -3.12 -m venv .venv }; .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\""

echo "[3/4] Running Windows tool script..."
"${ssh_base[@]}" \
  "${WINLAB_REPO_PATH}\\.venv\\Scripts\\python.exe ${WINLAB_REPO_PATH}\\test_windows_tools.py"

echo "[4/4] Running Windows control/integration pytest suite..."
"${ssh_base[@]}" \
  "${WINLAB_REPO_PATH}\\.venv\\Scripts\\python.exe -m pytest ${WINLAB_REPO_PATH}\\tests\\test_control.py ${WINLAB_REPO_PATH}\\tests\\test_integration.py -q"

echo "Windows validation complete."
