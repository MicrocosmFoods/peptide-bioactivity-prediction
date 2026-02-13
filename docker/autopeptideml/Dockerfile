# python 3.11.8 full image
FROM python:3.11.8

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    libpython3-dev \
    && rm -rf /var/lib/apt/lists/*

# pip install setup
RUN pip install --no-cache-dir -U pip setuptools wheel

# install autopeptideml
RUN pip install --no-cache-dir \
    "autopeptideml==2.0.5" \
    pandas \
    biopython

# cleanup
RUN apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*