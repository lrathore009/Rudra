#!/usr/bin/env bash
# Download Solar System Scope 2K textures (CC BY 4.0 — https://www.solarsystemscope.com/textures/)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/../frontend/public/textures/planets" && pwd)"
mkdir -p "$DIR"
BASE="https://www.solarsystemscope.com/textures/download"

download() {
  local name="$1"
  local ext="${2:-jpg}"
  echo "→ $name.$ext"
  curl -fsSL "$BASE/${name}.${ext}" -o "$DIR/${name}.${ext}"
}

download 2k_mercury
download 2k_venus_surface
download 2k_earth_daymap
download 2k_earth_clouds
download 2k_mars
download 2k_jupiter
download 2k_saturn
download 2k_saturn_ring_alpha png
download 2k_uranus
download 2k_neptune
download 2k_moon
download 2k_sun
download 2k_stars_milky_way

echo "Done — $(ls "$DIR" | wc -l | tr -d ' ') textures in $DIR"
