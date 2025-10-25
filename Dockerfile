# ====================================================================
# STAGE 1: THE BUILDER STAGE
# Used for installing all necessary build tools and compiling GUFI.
# We keep all dependencies here, even the large ones, as this stage is discarded.
# ====================================================================
FROM python:3.13-slim AS builder

# 1. INSTALL ALL SYSTEM DEPENDENCIES
# We install everything needed for GUFI compilation in a single efficient layer.
RUN apt-get update && \
    apt-get install -y \
        git \
        cmake \
        build-essential \
        graphviz \
        libgraphviz-dev \
        bsdmainutils \
        attr \
        libsqlite3-dev \
        libacl1-dev \
        libpcre2-dev \
        zlib1g-dev \
        libjson-c-dev \
        libgomp1 \
        pkg-config \
        autoconf \
        automake \
        \
        && rm -rf /var/lib/apt/lists/*

# 2. BUILD AND INSTALL GUFI
# GUFI binaries will be installed to /usr/local/bin within this stage.
WORKDIR /usr/local/src/gufi
RUN git clone https://github.com/mar-file-system/GUFI.git .
RUN mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# 3. INSTALL PYTHON DEPENDENCIES
# Installing everything we need to run the FileSystemAnalysis workflow
WORKDIR /app
RUN pip3 install zss matplotlib igraph networkx pygraphviz reportlab

# ====================================================================
# STAGE 2: THE FINAL RUNTIME STAGE
# Uses a fresh, minimal python:3.13-slim image and copies only artifacts.
# The final image will NOT contain git, cmake, or the build tools.
# ====================================================================
FROM python:3.13-slim

# 1. Set the application working directory
WORKDIR /app

# 2. COPY COMPILED ARTIFACTS from the builder stage:

# a. GUFI Binaries (Executables)
COPY --from=builder /usr/local/bin/gufi_* /usr/local/bin/

# b. GUFI Libraries (Crucial for runtime linking)
# We copy all libraries to ensure any dynamic links required by the GUFI binaries are found.
COPY --from=builder /usr/local/lib/ /usr/local/lib/

# c. Python Site Packages
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# 3. COPY MAIN REPO FILES
COPY . /app

# 4. DIRECTORY AND PERMISSION SETUP
RUN mkdir -p /app/data /app/report/data /app/report/images && \
    chmod +x /app/src/run_workflow.sh

# 5. Set the working directory to src so the user can run scripts with a simple relative path
WORKDIR /app/src
