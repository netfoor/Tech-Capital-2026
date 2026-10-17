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

# La plataforma no se publica sin acceso: una compilación sin Cognito queda en modo local (ADR-0009).
# Excepción temporal y explícita (T010-09 pendiente): PERMITIR_SIN_ACCESO=1 make desplegar
if ! grep -rqs "amazoncognito.com" "$DIST/_astro"; then
  if [[ "${PERMITIR_SIN_ACCESO:-0}" == "1" ]]; then
    echo "Aviso: se publica en modo local, sin inicio de sesión (PERMITIR_SIN_ACCESO=1)." >&2
  else
    echo "web/dist se compiló en modo local, sin Cognito. Corre: make web-config && make web" >&2
    echo "Para publicar sin inicio de sesión de forma temporal: PERMITIR_SIN_ACCESO=1 make desplegar" >&2
    exit 1
  fi
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
