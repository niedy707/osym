#!/usr/bin/env bash
# Vercel'e yayın + sabit alias'ı yeni deployment'a bağla.
# osym-yks.vercel.app bir proje alan adı degil, alias oldugu icin her prod
# yayinindan sonra yeniden baglanmasi gerekir; bu script onu unutulmaz kilar.
set -euo pipefail
cd "$(dirname "$0")"
echo "→ Vercel prod yayını…"
DEP=$(vercel --prod --yes 2>&1 | grep -o 'https://osym-[a-z0-9]*-niedy707s-projects\.vercel\.app' | tail -1)
[ -z "$DEP" ] && { echo "HATA: deployment URL'i alınamadı"; exit 1; }
echo "→ deployment: $DEP"
for A in osym-yks.vercel.app osym-tau.vercel.app; do
  vercel alias set "$DEP" "$A" >/dev/null 2>&1 && echo "→ alias bağlandı: $A" || echo "UYARI: alias bağlanamadı: $A"
done
echo "→ doğrulama:"
for A in osym-yks.vercel.app osym-tau.vercel.app; do
  printf '   %-26s HTTP %s\n' "$A" "$(curl -s -o /dev/null -w '%{http_code}' "https://$A/?v=$RANDOM")"
done
