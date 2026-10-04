#!/usr/bin/env bash
# Checks that your operating system is supported and that every tool this
# repository needs is installed - see REQUIREMENTS.md, section 1 (supported
# operating systems) and section 3 (software), which this script's checks
# and version numbers are kept in sync with.
#
# Run it with `make check` (see the Makefile) or directly:
#   bash scripts/check-deps.sh
#
# It never installs anything. Written for bash 3.2 (macOS's default
# /bin/bash) as well as newer bash - no associative arrays, no `${var,,}`,
# no `sort -V` (a GNU-only flag) - see ver_ge() below instead.

set -u

FAIL_COUNT=0
WARN_COUNT=0

# --- output helpers ----------------------------------------------------

if [ -t 1 ]; then
  C_OK="\033[32m"
  C_WARN="\033[33m"
  C_FAIL="\033[31m"
  C_RESET="\033[0m"
else
  C_OK=""
  C_WARN=""
  C_FAIL=""
  C_RESET=""
fi

section() {
  echo ""
  echo "== $1 =="
}

ok() {
  printf "  ${C_OK}[ OK ]${C_RESET} %s\n" "$1"
}

warn() {
  printf "  ${C_WARN}[WARN]${C_RESET} %s\n" "$1"
  WARN_COUNT=$((WARN_COUNT + 1))
}

fail() {
  printf "  ${C_FAIL}[FAIL]${C_RESET} %s\n" "$1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

# ver_ge HAVE WANT - true (exit 0) if version HAVE >= WANT, comparing
# dot-separated numeric fields (so "3.9" < "3.10", unlike a plain string
# compare). Implemented in plain awk instead of `sort -V` because macOS's
# default BSD `sort` doesn't support `-V` (a GNU coreutils extension) - see
# the file header.
ver_ge() {
  awk -v have="$1" -v want="$2" '
    BEGIN {
      n1 = split(have, h, ".")
      n2 = split(want, w, ".")
      max = (n1 > n2 ? n1 : n2)
      for (i = 1; i <= max; i++) {
        hv = (i <= n1) ? h[i] + 0 : 0
        wv = (i <= n2) ? w[i] + 0 : 0
        if (hv > wv) { exit 0 }
        if (hv < wv) { exit 1 }
      }
      exit 0
    }'
}

# first_version TEXT - extracts the first "N.N" or "N.N.N" substring found
# in TEXT (most --version outputs have exactly one, but some, like
# `aws --version`, have several - this picks the first, which is always the
# tool's own version in every command this script checks).
first_version() {
  echo "$1" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n 1
}

REQUIREMENTS_HINT="See REQUIREMENTS.md, section 3 (Software), for what this is for and the exact install command for your OS."

# --- operating system ----------------------------------------------------

check_os() {
  section "Operating system (REQUIREMENTS.md section 1)"

  os="$(uname -s)"
  arch="$(uname -m)"

  case "$os" in
    Linux)
      distro="unknown"
      distro_ver="unknown"
      if [ -r /etc/os-release ]; then
        # shellcheck disable=SC1091  # a real, standard system file - not part of this repo
        distro="$(. /etc/os-release && echo "$ID")"
        # shellcheck disable=SC1091
        distro_ver="$(. /etc/os-release && echo "$VERSION_ID")"
      fi
      if [ "$distro" != "ubuntu" ]; then
        warn "Detected Linux distro '$distro' ($arch) - this repository is tested on Ubuntu 22.04/24.04/26.04 (amd64). Other distros may still work; see REQUIREMENTS.md section 1."
      elif [ "$arch" != "x86_64" ]; then
        warn "Detected Ubuntu $distro_ver on '$arch' - this repository is tested on amd64 (x86_64); see REQUIREMENTS.md section 1."
      else
        case "$distro_ver" in
          22.04 | 24.04 | 26.04)
            ok "Ubuntu $distro_ver ($arch) - supported"
            ;;
          *)
            warn "Ubuntu $distro_ver ($arch) detected - this repository is tested on 22.04/24.04/26.04; $distro_ver is likely fine too, but see REQUIREMENTS.md section 1."
            ;;
        esac
      fi
      ;;
    Darwin)
      macos_ver="$(sw_vers -productVersion 2>/dev/null || echo "")"
      if [ "$arch" != "arm64" ] && [ "$arch" != "x86_64" ]; then
        warn "macOS on unexpected architecture '$arch' - see REQUIREMENTS.md section 1."
      elif [ -z "$macos_ver" ]; then
        warn "macOS ($arch) detected, but the version could not be determined."
      elif ver_ge "$macos_ver" "13.0"; then
        ok "macOS $macos_ver ($arch) - supported"
      else
        warn "macOS $macos_ver ($arch) detected - this repository targets macOS 13+; see REQUIREMENTS.md section 1."
      fi
      ;;
    *)
      fail "Operating system '$os' is not directly supported. Windows users: install WSL2 with an Ubuntu distro and re-run this check inside it - see REQUIREMENTS.md section 1."
      ;;
  esac
}

# --- software ------------------------------------------------------------

check_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not found on PATH - 'uv sync' downloads Python 3.14 by itself, or run 'mise install' (REQUIREMENTS.md section 3.3)."
    return
  fi
  have="$(first_version "$(python3 --version 2>&1)")"
  if [ -z "$have" ]; then
    warn "python3 found, but its version could not be parsed."
  elif ver_ge "$have" "3.14"; then
    ok "Python $have (3.14 pinned in .python-version/mise.toml)"
  else
    warn "Python $have found, but this repository pins 3.14 - run 'mise install', or let 'uv sync' download 3.14 itself (REQUIREMENTS.md sections 3.3 and 4)."
  fi
}

check_uv() {
  if ! command -v uv >/dev/null 2>&1; then
    fail "uv not found. $REQUIREMENTS_HINT"
    return
  fi
  have="$(first_version "$(uv --version 2>&1)")"
  ok "uv${have:+ $have} found"
}

check_go() {
  if ! command -v go >/dev/null 2>&1; then
    warn "go not found (only needed for the 5-golang-for-devops module) - run 'mise install' (REQUIREMENTS.md section 3.3)."
    return
  fi
  have="$(first_version "$(go version 2>&1)")"
  if [ -n "$have" ] && ver_ge "$have" "1.27"; then
    ok "Go $have (1.27 pinned in mise.toml and go.mod)"
  else
    warn "Go${have:+ $have} found, but 5-golang-for-devops/go.mod needs 1.27 - with the default GOTOOLCHAIN=auto, go downloads it; or run 'mise install'."
  fi
}

check_mise() {
  if ! command -v mise >/dev/null 2>&1; then
    warn "mise not found (recommended, not required - installs the pinned Python, uv and Go). See REQUIREMENTS.md section 3.3."
    return
  fi
  have="$(first_version "$(mise --version 2>&1)")"
  ok "mise${have:+ $have} found"
}

# A plain "is it on PATH?" check: required tools fail, optional ones warn.
check_command() {
  name="$1"; level="$2"; why="$3"
  if command -v "$name" >/dev/null 2>&1; then
    ok "$name found"
  elif [ "$level" = "required" ]; then
    fail "$name not found ($why). $REQUIREMENTS_HINT"
  else
    warn "$name not found (optional - $why; see REQUIREMENTS.md section 3)."
  fi
}

# --- configuration ---------------------------------------------------------

# Reads one variable from .env without executing the file.
env_value() {
  grep -E "^$1=" .env 2>/dev/null | tail -n 1 | cut -d= -f2-
}

check_env_file() {
  if [ ! -f .env ]; then
    warn ".env not found - run 'cp .env.example .env' (REQUIREMENTS.md section 5). Until then the examples run only with LLM_PROVIDER=fake."
    return
  fi
  ok ".env found"
  provider="${LLM_PROVIDER:-$(env_value LLM_PROVIDER)}"
  provider="${provider:-google_genai}"
  case "$provider" in
    fake)
      ok "LLM_PROVIDER=fake - offline mode, no API key needed"
      ;;
    google_genai | openai)
      if [ "$provider" = "google_genai" ]; then key_name="GOOGLE_API_KEY"; else key_name="OPENAI_API_KEY"; fi
      key_value="$(env_value "$key_name")"
      if [ -z "$key_value" ] || [ "$key_value" = "your_google_api_key_here" ] || [ "$key_value" = "your_openai_api_key_here" ]; then
        warn "LLM_PROVIDER=$provider, but $key_name in .env is empty or still the placeholder (REQUIREMENTS.md section 5)."
      else
        ok "LLM_PROVIDER=$provider and $key_name is set"
      fi
      ;;
    *)
      fail "LLM_PROVIDER='$provider' is not one of google_genai, openai, fake (REQUIREMENTS.md section 5)."
      ;;
  esac
}

# --- main ------------------------------------------------------------------

check_os

section "Required software (REQUIREMENTS.md section 3)"
check_uv
check_python
check_command git required "clones this repository"
check_command make required "runs the Makefile shortcuts"
check_command curl required "installs uv and mise"

section "Recommended software"
check_mise
check_go

section "Configuration (REQUIREMENTS.md section 5)"
check_env_file

echo ""
echo "======================================================================"
if [ "$FAIL_COUNT" -gt 0 ]; then
  printf "${C_FAIL}%s missing/unsupported required item(s), %s warning(s).${C_RESET}\n" "$FAIL_COUNT" "$WARN_COUNT"
  echo ""
  echo "See REQUIREMENTS.md for what each [FAIL] item is for and the exact"
  echo "install command for your operating system (section 3)."
  echo "======================================================================"
  exit 1
else
  printf "${C_OK}All required software found and your operating system is supported${C_RESET} (%s warning(s) - see REQUIREMENTS.md for anything marked [WARN] above).\n" "$WARN_COUNT"
  echo "======================================================================"
  exit 0
fi
