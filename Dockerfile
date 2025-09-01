# Use PyTorch base image with CUDA support (Ubuntu 22.04 based)
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    conda clean -afy

# Create conda environment with Python 3.12
# Accept Anaconda TOS for default channels
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda create -n diffusion-pipe python=3.12 -y -c conda-forge

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "diffusion-pipe", "/bin/bash", "-c"]

# Upgrade to the specific PyTorch version required by the project
RUN pip install --upgrade torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128

# Install CUDA nvcc compiler
RUN conda install -n diffusion-pipe -c nvidia cuda-nvcc=12.8 -y

# Set working directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the entire project
COPY . .

# Initialize and update git submodules
RUN git submodule init && git submodule update --recursive || true

# Set environment variables for NCCL (required for RTX 4000 series)
ENV NCCL_P2P_DISABLE=1
ENV NCCL_IB_DISABLE=1

# Enable expandable segments for CUDA memory allocator (helps with VRAM optimization)
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Activate conda environment by default
RUN echo "conda activate diffusion-pipe" >> ~/.bashrc

# Default command
CMD ["conda", "run", "-n", "diffusion-pipe", "bash"]