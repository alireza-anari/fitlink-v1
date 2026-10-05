# Official MinIO source build; no third-party binary mirror.
FROM library/golang@sha256:a688600ca24f8a4d3ca77f95b0dd40704a9fc787c826660eb7ba0b641b8b175d AS builder
ADD --checksum=sha256:45521908307306e925c98d629e1c17d78c8b72b6ee242b1bfb1409f7d8ee5841 https://codeload.github.com/minio/minio/tar.gz/9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a /tmp/source.tar.gz
RUN mkdir /src && tar -xzf /tmp/source.tar.gz -C /src --strip-components=1
WORKDIR /src
ENV GOTOOLCHAIN=local CGO_ENABLED=0
RUN go build -mod=readonly -trimpath -o /out/minio .
FROM library/python@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS minio
RUN useradd --uid 1000 --create-home app && mkdir /data && chown app:app /data
COPY --from=builder /out/minio /usr/local/bin/minio
COPY --from=builder /src/LICENSE /licenses/minio/LICENSE
USER app
WORKDIR /data
ENTRYPOINT []
CMD ["minio", "server", "/data", "--quiet", "--console-address", ":9001"]
FROM library/python@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS mc
ADD --checksum=sha256:01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891 https://github.com/minio/mc/releases/download/RELEASE.2025-08-13T08-35-41Z/mc.linux-amd64.RELEASE.2025-08-13T08-35-41Z /usr/local/bin/mc
RUN chmod 755 /usr/local/bin/mc && useradd --uid 1000 --create-home app
USER app
ENTRYPOINT []
