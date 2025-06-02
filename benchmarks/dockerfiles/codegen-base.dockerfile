ARG TARGETPLATFORM=linux/amd64
FROM --platform=$TARGETPLATFORM ghcr.io/astral-sh/uv:python3.13-bookworm

# Set environment variables to prevent interactive prompts during installation
ENV NVM_DIR=/usr/local/nvm \
    NODE_VERSION=22.14.0 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_OPTIONS="--max-old-space-size=8192" \
    PYTHONUNBUFFERED=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    PYTHONPATH="/usr/local/lib/python3.13/site-packages" \
    IS_SANDBOX=True

ENV PATH=$NVM_DIR/versions/node/$NODE_VERSION/bin:/usr/local/nvm:/usr/local/bin:$PATH

ARG INVALIDATE_FILES_LAYER=1
# Copy configuration files and set permissions
COPY sshd_config /etc/ssh/sshd_config
COPY ssh_config /etc/ssh/ssh_config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start.sh /usr/local/bin/start.sh
COPY setup_ssh_user.sh /usr/local/bin/setup_ssh_user.sh
COPY setup_ssh_keys.sh /usr/local/bin/setup_ssh_keys.sh
COPY nginx.conf /etc/nginx/nginx.conf
COPY error.html /usr/share/nginx/html/error.html
COPY tmux_output_script.sh /usr/local/bin/tmux_output_script.sh

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
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p -m 755 /etc/apt/keyrings \
    && wget -nv -O- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    # Set up environment variables and save it to /etc/profile.d/nvm.sh
    && echo "export NVM_DIR=\"$NVM_DIR\"" >> /etc/profile.d/nvm.sh \
    && echo "[ -s \"$NVM_DIR/nvm.sh\" ] && \. \"$NVM_DIR/nvm.sh\"" >> /etc/profile.d/nvm.sh \
    && echo "export PATH=\"$NVM_DIR/versions/node/$NODE_VERSION/bin:\$PATH\"" >> /etc/profile.d/nvm.sh \
    && echo "export NVM_BIN=\"$NVM_DIR/versions/node/$NODE_VERSION/bin\"" >> /etc/profile.d/nvm.sh \
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
    && chmod +x /etc/profile.d/nvm.sh \
    # Run the SSH setup script
    && /usr/local/bin/setup_ssh_user.sh \
    # Install nvm, Node.js, and code-server
    && mkdir -p $NVM_DIR \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm use $NODE_VERSION \
    && npm install -g yarn pnpm \
    && corepack enable \
    && corepack prepare yarn@stable --activate \
    && corepack prepare pnpm@latest --activate \
    && curl -fsSL https://raw.githubusercontent.com/coder/code-server/refs/tags/v4.99.1/install.sh | sh \
    && uv tool install uvicorn[standard]

ENTRYPOINT ["/usr/local/bin/start.sh"]
