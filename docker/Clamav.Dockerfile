# Official patched ClamAV 1.5.4_base, immutable upstream multi-platform digest.
FROM clamav/clamav@sha256:7769870154c74ce31b0047dd8771e81f7c4269278bc005782e9e419e4922c73d
USER root
COPY docker/clamd.c03.conf /etc/clamav/clamd.c03.conf
RUN mkdir -p /var/lib/clamav /run/clamav && chown -R clamav:clamav /var/lib/clamav /run/clamav
USER clamav
ENTRYPOINT []
CMD ["clamd", "--foreground=true", "--config-file=/etc/clamav/clamd.c03.conf"]
