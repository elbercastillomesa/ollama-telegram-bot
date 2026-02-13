# ollama-telegram-bot

This is an experiment to create an AI assitant on my Odroid C2+ (old hardware I know), using Ollama
currntly the model gemma3:1b and integrate it using Telegram.

## Requirements

Install necessary packages to build Python from source,

```bash
apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
```

### Download Python Source Code

Visit the Python downloads page to get the source code. Then, using wget, download the source,

Then download python from the official website

- https://www.python.org/downloads/release/python-31212/

```bash
wget https://www.python.org/ftp/python/3.12.12/Python-3.12.12.tgz
```

Now, Extract the Archive,

```bash
tar -xf Python-3.12.12.tgz
```

Configure and Build,

```bash
cd Python-3.12.12
./configure --enable-optimizations
```

Build Python,

```bash
make -j 4
# Replace 4 with the number of CPU cores you want to allocate for the build process.
```

Install Python

```bash
make altinstall
```

Using altinstall instead of install prevents it from replacing the system's default Python interpreter (which could cause system tools to malfunction).

### Install Python libraries

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Set the Environment Variables

Copy the variables file and fill the required data.

```bash
cp .env.local .env
```

--- 

### Run the app

```bash
python telegram_assitant.py
```