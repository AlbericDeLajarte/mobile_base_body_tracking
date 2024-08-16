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
    iptables

# Install pyenv and Python 3.10
curl https://pyenv.run | bash

# Add to bashrc and restart shell
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv install 3.10.0 && pyenv global 3.10.0

# Install dependencies
pip install -r requirements.txt

