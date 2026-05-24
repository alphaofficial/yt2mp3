#!/usr/bin/env sh
set -eu

REPO="${YT2MP3_REPO:-alphaofficial/yt2mp3}"
YT2MP3_HOME="${YT2MP3_HOME:-$HOME/.yt2mp3}"
BIN_DIR="$YT2MP3_HOME/bin"
BIN_PATH="$BIN_DIR/yt2mp3"

os="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$os" in
  darwin) os="darwin" ;;
  linux) os="linux" ;;
  *) echo "Unsupported OS: $os" >&2; exit 1 ;;
esac

arch="$(uname -m | tr '[:upper:]' '[:lower:]')"
case "$arch" in
  x86_64|amd64) arch="amd64" ;;
  arm64|aarch64) arch="arm64" ;;
  *) echo "Unsupported architecture: $arch" >&2; exit 1 ;;
esac

artifact="yt2mp3-${os}-${arch}"
url="https://github.com/${REPO}/releases/latest/download/${artifact}"

echo "Installing yt2mp3 from $url"
mkdir -p "$BIN_DIR"
tmp="$(mktemp "$BIN_DIR/yt2mp3.XXXXXX")"
cleanup() { rm -f "$tmp"; }
trap cleanup EXIT

curl -fsSL "$url" -o "$tmp"
chmod +x "$tmp"
mv "$tmp" "$BIN_PATH"
trap - EXIT

if command -v xattr >/dev/null 2>&1 && [ "$os" = "darwin" ]; then
  xattr -dr com.apple.quarantine "$BIN_PATH" 2>/dev/null || true
fi

echo "yt2mp3 installed to $BIN_PATH"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo "Add yt2mp3 to your PATH:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
    if [ -n "${SHELL:-}" ]; then
      rc="$HOME/.profile"
      case "$SHELL" in
        */zsh) rc="$HOME/.zshrc" ;;
        */bash) rc="$HOME/.bashrc" ;;
      esac
      printf "Update %s? [y/N] " "$rc"
      read ans || ans=""
      case "$ans" in
        y|Y|yes|YES)
          printf '\n# yt2mp3\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$rc"
          echo "Updated $rc"
          ;;
      esac
    fi
    ;;
esac

echo "Run: yt2mp3 --help"
