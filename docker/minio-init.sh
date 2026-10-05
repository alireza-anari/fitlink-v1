#!/bin/sh
set -eu
# No xtrace; mc configuration and policy live only in this ephemeral container.
i=0
until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1 && mc ready local >/dev/null 2>&1; do
  i=$((i+1)); [ "$i" -lt 30 ] || exit 1
  sleep 2
done
mc mb --ignore-existing local/fitlink-private >/dev/null
mc anonymous set none local/fitlink-private >/dev/null
cat >/tmp/policy.json <<'JSON'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:ListBucket","s3:GetBucketLocation"],"Resource":["arn:aws:s3:::fitlink-private"]},{"Effect":"Allow","Action":["s3:GetObject","s3:PutObject","s3:DeleteObject"],"Resource":["arn:aws:s3:::fitlink-private/*"]}]}
JSON
mc admin policy create local foundation-private /tmp/policy.json >/dev/null
mc admin user add local "$MINIO_APP_ACCESS_KEY" "$MINIO_APP_SECRET_KEY" >/dev/null
mc admin policy attach local foundation-private --user "$MINIO_APP_ACCESS_KEY" >/dev/null
rm /tmp/policy.json
