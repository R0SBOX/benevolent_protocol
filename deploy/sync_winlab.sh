#!/usr/bin/env bash
set -euo pipefail

WINLAB_HOST="${WINLAB_HOST:-192.168.122.248}"
WINLAB_USER="${WINLAB_USER:-John}"
WINLAB_KEY="${WINLAB_KEY:-$HOME/.ssh/id_ed25519}"
WINLAB_KNOWN_HOSTS="${WINLAB_KNOWN_HOSTS:-/tmp/benevolent_known_hosts}"
WINLAB_REPO_PATH="${WINLAB_REPO_PATH:-C:/Users/John/benevolent_protocol}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
archive_path="/tmp/benevolent_protocol-winlab.tar.gz"

echo "[1/3] Building repo snapshot from HEAD..."
git -C "$repo_root" archive --format=tar HEAD | gzip > "$archive_path"

echo "[2/3] Copying archive to ${WINLAB_USER}@${WINLAB_HOST}..."
scp -i "$WINLAB_KEY" \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile="$WINLAB_KNOWN_HOSTS" \
  "$archive_path" \
  "${WINLAB_USER}@${WINLAB_HOST}:C:/Users/John/"

echo "[3/3] Extracting snapshot into ${WINLAB_REPO_PATH}..."
ssh -i "$WINLAB_KEY" \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile="$WINLAB_KNOWN_HOSTS" \
  "${WINLAB_USER}@${WINLAB_HOST}" \
  "cmd /c if exist ${WINLAB_REPO_PATH//\//\\\\} rmdir /s /q ${WINLAB_REPO_PATH//\//\\\\} & mkdir ${WINLAB_REPO_PATH//\//\\\\} & tar -xzf C:\\Users\\John\\benevolent_protocol-winlab.tar.gz -C ${WINLAB_REPO_PATH//\//\\\\}"

echo "Sync complete."
