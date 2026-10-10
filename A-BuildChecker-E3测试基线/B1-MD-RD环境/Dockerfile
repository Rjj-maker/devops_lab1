FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        make \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY main.c \
     config.h \
     unused.h \
     Makefile \
     README.md \
     interface.json \
     ./

RUN make \
    && test -x ./app

LABEL org.opencontainers.image.title="E3 BuildChecker MD/RD environment" \
      org.opencontainers.image.source="https://github.com/Rowan-hhh/devops_lab1" \
      org.opencontainers.image.revision="29c02d6604d7071d4b249ec958dd8a553caa670a" \
      dev.devops-lab.project="e3-buildchecker-md-rd@2026-09-10"

CMD ["./app"]
