# import full python image
FROM python:3.14.3

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

# install autopeptideml v2.0.6 from github source
RUN pip install git+https://github.com/IBM/AutoPeptideML

# cleanup
RUN apt-get remove -y git gcc g++ make libpython3-dev && apt-get autoremove -y

# environment path
ENV PATH="/app/autopeptideml/scripts:${PATH}"
