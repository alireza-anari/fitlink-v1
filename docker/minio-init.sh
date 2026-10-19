#!/bin/sh
set -eu
bootstrap_phase=alias
trap 'status=$?; if [ "$status" -ne 0 ]; then printf "C04_STORAGE_BOOTSTRAP %s failure %s\n" "$bootstrap_phase" "$status"; fi' EXIT
# No xtrace; mc configuration and policy live only in this ephemeral container.
bootstrap_ready() {
  bootstrap_phase=alias
  mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1 || return 1
  bootstrap_phase=ready
  mc ready local >/dev/null 2>&1 || return 1
}
i=0
until bootstrap_ready; do
  i=$((i+1)); [ "$i" -lt 30 ] || exit 1
  sleep 2
done
bootstrap_phase=mb
mc mb --ignore-existing local/fitlink-private >/dev/null
bootstrap_phase=anonymous
mc anonymous set none local/fitlink-private >/dev/null
bootstrap_phase=policy
cat >/tmp/policy.json <<'JSON'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:ListBucket","s3:GetBucketLocation"],"Resource":["arn:aws:s3:::fitlink-private"]},{"Effect":"Allow","Action":["s3:GetObject","s3:PutObject","s3:DeleteObject"],"Resource":["arn:aws:s3:::fitlink-private/*"]}]}
JSON
mc admin policy create local foundation-private /tmp/policy.json >/dev/null
bootstrap_phase=user
mc admin user add local "$MINIO_APP_ACCESS_KEY" "$MINIO_APP_SECRET_KEY" >/dev/null
bootstrap_phase=attach
mc admin policy attach local foundation-private --user "$MINIO_APP_ACCESS_KEY" >/dev/null
bootstrap_phase=cleanup
rm /tmp/policy.json
printf 'C04_STORAGE_BOOTSTRAP complete success 0\n'
