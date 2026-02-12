# python full image
FROM python:3.8.20

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

# pip install package dependencies
RUN pip install biopython==1.78 keras==2.4.3 tensorflow==2.2.0 protobuf==3.20.0 numpy==1.23.5

# pip install deepsig
RUN pip install deepsig-biocomp

# cleanup
RUN apt-get remove -y git gcc g++ make libpython3-dev && apt-get autoremove -y

# environment path
ENV DEEPSIG_ROOT=/usr/local/lib/python3.8/site-packages/deepsig