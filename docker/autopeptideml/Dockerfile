FROM python:3.11-slim

WORKDIR /app

# OS deps needed for downloading + extracting mmseqs2
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        tar \
        libgomp1; \
    rm -rf /var/lib/apt/lists/*

# Install MMseqs2 (AVX2; swap to sse41 if needed)
RUN set -eux; \
    wget -O /tmp/mmseqs.tar.gz https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz; \
    tar xzf /tmp/mmseqs.tar.gz -C /tmp; \
    mv /tmp/mmseqs/bin/mmseqs /usr/local/bin/mmseqs; \
    rm -rf /tmp/mmseqs /tmp/mmseqs.tar.gz

# Python deps (no cache)
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir \
      scikit-learn==1.3.0 \
      biopython==1.83 \
      pandas \
      autopeptideml==1.0.1

ENV PATH="/app/autopeptideml/scripts:${PATH}"
