# import full python image
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
# install dependencies
RUN pip install scikit-learn==1.3.0 biopython==1.83 pandas

# install autopeptideml v1.0.1
RUN pip install autopeptideml==1.0.1

# cleanup
RUN apt-get remove -y git gcc g++ make libpython3-dev && apt-get autoremove -y

# environment path
ENV PATH="/app/autopeptideml/scripts:${PATH}"
