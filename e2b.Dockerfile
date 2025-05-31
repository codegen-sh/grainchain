# Custom E2B Dockerfile for Outline Development
# This Dockerfile creates a sandbox template optimized for Outline (Node.js project)

FROM e2bdev/code-interpreter:latest

# Update package lists
RUN apt-get update

# Install Node.js 18 (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
    apt-get install -y nodejs

# Install Yarn package manager
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install -y yarn

# Install essential development tools
RUN apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    make \
    g++ \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree

# Install global Node.js packages commonly used with Outline
RUN npm install -g \
    npm@latest \
    typescript \
    ts-node \
    nodemon \
    prettier \
    eslint

# Set up workspace directory
WORKDIR /workspace

# Create cache directories to speed up subsequent installs
RUN mkdir -p /tmp/yarn-cache /tmp/npm-cache

# Set environment variables for development
ENV NODE_ENV=development
ENV YARN_CACHE_FOLDER=/tmp/yarn-cache
ENV NPM_CONFIG_CACHE=/tmp/npm-cache
ENV WORKSPACE=/workspace

# Ensure the user has proper permissions
RUN chown -R user:user /workspace /tmp/yarn-cache /tmp/npm-cache

# Switch to non-root user for security
USER user

# Create common project structure
RUN mkdir -p /workspace/projects

# Set default working directory
WORKDIR /workspace

# Add helpful aliases for development
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -la"' >> ~/.bashrc && \
    echo 'alias ..="cd .."' >> ~/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> ~/.bashrc

# Display versions for verification
RUN echo "=== Environment Setup Complete ===" && \
    node --version && \
    npm --version && \
    yarn --version && \
    git --version && \
    python3 --version
