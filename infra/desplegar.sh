#!/usr/bin/env bash
# Sube web/dist/ al bucket del sitio e invalida la caché de CloudFront (FR-010-05).
# Uso: make desplegar   (o PERFIL=otro-perfil ./infra/desplegar.sh)
set -euo pipefail

PERFIL="${PERFIL:-Fortino-IAM-Admin}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$RAIZ/web/dist"

if [[ ! -f "$DIST/index.html" ]]; then
  echo "No existe web/dist/index.html. Compila primero el sitio con: make web" >&2
  exit 1
fi

# Sin Cognito la compilación queda en modo local (ADR-0009).
# TEMPORAL (decisión del 2026-10-17, T010-09 y T010-10): se publica en modo local con un aviso.
# Al aplicar Cognito, reemplazar el aviso por el bloqueo de abajo:
#   echo "web/dist se compiló en modo local, sin Cognito. Corre: make web-config && make web" >&2
#   exit 1
if ! grep -rqs "amazoncognito.com" "$DIST/_astro"; then
  echo "Aviso: se publica en modo local, sin inicio de sesión (Cognito pendiente, T010-09)." >&2
fi

cd "$RAIZ/infra"
BUCKET="$(terraform output -raw bucket_sitio)"
DISTRIBUCION="$(terraform output -raw cloudfront_id)"
URL="$(terraform output -raw url)"

# 1. Recursos con huella en el nombre: caché de un año. Se suben primero para que el HTML nuevo los encuentre.
aws s3 sync "$DIST/_astro" "s3://$BUCKET/_astro" --profile "$PERFIL" \
  --cache-control "public,max-age=31536000,immutable"

# 2. HTML, datos y descargas: siempre se revalidan.
aws s3 sync "$DIST" "s3://$BUCKET" --profile "$PERFIL" --delete \
  --exclude "_astro/*" --exclude "*.csv" \
  --cache-control "no-cache"

# 3. CSV con su codificación declarada, para que los acentos se lean bien al abrirlos.
aws s3 sync "$DIST" "s3://$BUCKET" --profile "$PERFIL" --delete \
  --exclude "*" --include "*.csv" \
  --content-type "text/csv; charset=utf-8" --cache-control "no-cache"

# 4. Limpia recursos de despliegues anteriores.
aws s3 sync "$DIST/_astro" "s3://$BUCKET/_astro" --profile "$PERFIL" --delete \
  --cache-control "public,max-age=31536000,immutable"

aws cloudfront create-invalidation --profile "$PERFIL" \
  --distribution-id "$DISTRIBUCION" --paths "/*" \
  --query "Invalidation.Id" --output text

echo "Sitio publicado: $URL"
