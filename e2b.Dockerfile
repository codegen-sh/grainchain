# Custom E2B Dockerfile for Outline Development
# This Dockerfile creates a sandbox template optimized for Outline (Node.js project)

ARG TARGETPLATFORM=linux/amd64
FROM --platform=$TARGETPLATFORM e2bdev/code-interpreter:latest

# Set environment variables to prevent interactive prompts during installation
ENV NVM_DIR=/home/user/.nvm \
    NODE_VERSION=20.18.0 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_OPTIONS="--max-old-space-size=8192" \
    PYTHONUNBUFFERED=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    PYTHONPATH="/usr/local/lib/python3.13/site-packages" \
    IS_SANDBOX=True

ENV PATH=$NVM_DIR/versions/node/$NODE_VERSION/bin:/root/.local/bin:/usr/local/nvm:/usr/local/bin:$PATH

# Start as root for system-level installations
USER root

# Install dependencies and set up environment in a single layer
RUN apt-get update && apt-get install -y -o Dpkg::Options::="--force-confold" \
    git \
    curl \
    fd-find \
    gh \
    lsof \
    ripgrep \
    openssh-server \
    nginx-full \
    fcgiwrap \
    tmux \
    nano \
    vim \
    supervisor \
    netcat-openbsd \
    build-essential \
    python3 \
    python3-pip \
    make \
    g++ \
    wget \
    unzip \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p -m 755 /etc/apt/keyrings \
    && wget -nv -O- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Set up global environment variables and save to profile
RUN echo "export NVM_DIR=\"/home/user/.nvm\"" >> /etc/profile.d/nvm.sh \
    && echo "[ -s \"/home/user/.nvm/nvm.sh\" ] && . \"/home/user/.nvm/nvm.sh\"" >> /etc/profile.d/nvm.sh \
    && echo "export PATH=\"/home/user/.nvm/versions/node/$NODE_VERSION/bin:\$PATH\"" >> /etc/profile.d/nvm.sh \
    && echo "export NVM_BIN=\"/home/user/.nvm/versions/node/$NODE_VERSION/bin\"" >> /etc/profile.d/nvm.sh \
    && echo "export NODE_VERSION=\"$NODE_VERSION\"" >> /etc/profile.d/nvm.sh \
    && echo "export NODE_OPTIONS=\"--max-old-space-size=8192\"" >> /etc/profile.d/nvm.sh \
    && echo "export DEBIAN_FRONTEND=noninteractive" >> /etc/profile.d/nvm.sh \
    && echo "export PYTHONUNBUFFERED=1" >> /etc/profile.d/nvm.sh \
    && echo "export COREPACK_ENABLE_DOWNLOAD_PROMPT=0" >> /etc/profile.d/nvm.sh \
    && echo "export PYTHONPATH=\"/usr/local/lib/python3.13/site-packages\"" >> /etc/profile.d/nvm.sh \
    && echo "export IS_SANDBOX=true" >> /etc/profile.d/nvm.sh \
    && echo "export NPM_CONFIG_YES=true" >> /etc/profile.d/nvm.sh \
    && echo "export PIP_NO_INPUT=1" >> /etc/profile.d/nvm.sh \
    && echo "export YARN_ENABLE_IMMUTABLE_INSTALLS=false" >> /etc/profile.d/nvm.sh \
    && echo "export PATH=\"/root/.local/bin:\$PATH\"" >> /etc/profile.d/nvm.sh \
    && chmod +x /etc/profile.d/nvm.sh

# Install uv (Python package manager) and uvicorn as root
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="/root/.local/bin:$PATH"' >> /etc/profile.d/nvm.sh \
    && export PATH="/root/.local/bin:$PATH" \
    && uv tool install uvicorn[standard]

# Create workspace directories and set permissions
RUN mkdir -p /home/user/workspace /home/user/projects /home/user/.nvm

# Install nvm, Node.js, and package managers (as root but in user directory)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | NVM_DIR="/home/user/.nvm" bash \
    && export NVM_DIR="/home/user/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" \
    && nvm install $NODE_VERSION \
    && nvm use $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && npm install -g yarn@latest pnpm@latest \
    && echo "Node.js and package managers installed successfully"

# Install global Node.js development tools
RUN export NVM_DIR="/home/user/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" \
    && npm install -g \
        npm@latest \
        typescript \
        ts-node \
        nodemon \
        prettier \
        eslint

# Set up user bashrc for when E2B creates the user
RUN echo "export NVM_DIR=\"\$HOME/.nvm\"" >> /home/user/.bashrc \
    && echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\"" >> /home/user/.bashrc \
    && echo "[ -s \"\$NVM_DIR/bash_completion\" ] && . \"\$NVM_DIR/bash_completion\"" >> /home/user/.bashrc \
    && echo "export PATH=\"/root/.local/bin:\$HOME/.local/bin:\$PATH\"" >> /home/user/.bashrc \
    && echo "export NODE_OPTIONS=\"--max-old-space-size=8192\"" >> /home/user/.bashrc \
    && echo "export NPM_CONFIG_YES=true" >> /home/user/.bashrc \
    && echo "export PIP_NO_INPUT=1" >> /home/user/.bashrc \
    && echo "export YARN_ENABLE_IMMUTABLE_INSTALLS=false" >> /home/user/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/user/.bashrc \
    && echo 'alias la="ls -la"' >> /home/user/.bashrc \
    && echo 'alias ..="cd .."' >> /home/user/.bashrc \
    && echo 'alias grep="grep --color=auto"' >> /home/user/.bashrc \
    && chmod -R 755 /home/user

# Set working directory
WORKDIR /home/user/workspace

# Verify installation and display versions
RUN export NVM_DIR="/home/user/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" \
    && echo "=== E2B Codegen Environment Setup Complete ===" \
    && node --version \
    && npm --version \
    && yarn --version \
    && pnpm --version \
    && python3 --version \
    && echo "Environment ready for development!"
