#!/usr/bin/env bash
set -euo pipefail

WINLAB_HOST="${WINLAB_HOST:-192.168.122.248}"
WINLAB_USER="${WINLAB_USER:-John}"
WINLAB_KEY="${WINLAB_KEY:-$HOME/.ssh/id_ed25519}"
WINLAB_KNOWN_HOSTS="${WINLAB_KNOWN_HOSTS:-/tmp/benevolent_known_hosts}"
WINLAB_REPO_PATH="${WINLAB_REPO_PATH:-C:\\Users\\John\\benevolent_protocol}"
WINLAB_VENV_PATH="${WINLAB_VENV_PATH:-C:\\Users\\John\\.benevolent_protocol_venv}"
WINLAB_STATE_DIR="${WINLAB_STATE_DIR:-C:\\Users\\John\\.benevolent_protocol_winlab}"

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
  "powershell -NoProfile -Command \"\
    \$repo = '${WINLAB_REPO_PATH}'; \
    \$venv = '${WINLAB_VENV_PATH}'; \
    \$stateDir = '${WINLAB_STATE_DIR}'; \
    \$stamp = Join-Path \$stateDir 'requirements.sha256'; \
    \$requirements = Join-Path \$repo 'requirements.txt'; \
    if (-not (Test-Path \$stateDir)) { New-Item -ItemType Directory -Force -Path \$stateDir | Out-Null }; \
    if (-not (Test-Path \$venv\\Scripts\\python.exe)) { py -3.12 -m venv \$venv }; \
    \$currentHash = (Get-FileHash \$requirements -Algorithm SHA256).Hash; \
    \$savedHash = ''; \
    if (Test-Path \$stamp) { \$savedHash = (Get-Content \$stamp -Raw).Trim() }; \
    if (\$currentHash -ne \$savedHash) { \
      & \$venv\\Scripts\\python.exe -m pip install -r \$requirements; \
      Set-Content -Path \$stamp -Value \$currentHash; \
      Write-Host 'Dependencies updated.'; \
    } else { \
      Write-Host 'Dependencies unchanged; skipping pip install.'; \
    }\""

echo "[3/4] Running Windows tool script..."
"${ssh_base[@]}" \
  "${WINLAB_VENV_PATH}\\Scripts\\python.exe ${WINLAB_REPO_PATH}\\test_windows_tools.py"

echo "[4/4] Running Windows control/integration/runtime pytest suite..."
"${ssh_base[@]}" \
  "${WINLAB_VENV_PATH}\\Scripts\\python.exe -m pytest ${WINLAB_REPO_PATH}\\tests\\test_control.py ${WINLAB_REPO_PATH}\\tests\\test_integration.py ${WINLAB_REPO_PATH}\\tests\\test_orchestrator_runtime.py -q"

echo "Windows validation complete."
