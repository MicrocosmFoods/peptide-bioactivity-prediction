# python full image
FROM python:3.11.8

WORKDIR /app

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    libpython3-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install MMseqs2
RUN wget https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz && \
    tar xvfz mmseqs-linux-avx2.tar.gz && \
    mv mmseqs/bin/mmseqs /usr/local/bin/ && \
    rm -rf mmseqs mmseqs-linux-avx2.tar.gz

# pip install package dependencies
RUN pip install scikit-learn==1.3.0 biopython==1.83 pandas==2.1.1

# pip install autopeptideml
RUN pip install autopeptideml==1.0.1

# cleanup
RUN apt-get remove -y git gcc g++ make libpython3-dev wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/app/autopeptideml/scripts:${PATH}"
