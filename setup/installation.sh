#!/bin/bash

# Update and install necessary packages
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev \
    libsqlite3-dev \
    liblzma-dev \
    libncursesw5-dev \
    libgdbm-compat-dev \
    tk-dev \
    libdb5.3-dev \
    libexpat1-dev \
    iptables \
    dhcpcd5

# Install pyenv
curl https://pyenv.run | bash

# Pyenv initialization commands
PYENV_INIT='export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"'

# Add pyenv initialization to .bashrc if not already present
if ! grep -q 'export PATH="$HOME/.pyenv/bin:$PATH"' ~/.bashrc; then
    echo "$PYENV_INIT" >> ~/.bashrc
fi

# Apply pyenv initialization for the current session
eval "$PYENV_INIT"

# Install Python 3.10
pyenv install 3.10.0
pyenv global 3.10.0

# Install dependencies
pip install -r requirements.txt
