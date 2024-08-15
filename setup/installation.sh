# Install pyenv and Python 3.10
curl https://pyenv.run | bash

# Add to bashrc and restart shell
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

exec "$SHELL"

pyenv install 3.10.0 && pyenv global 3.10.0

# Create virtual environment
python venv teleop_venv
source teleop_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

