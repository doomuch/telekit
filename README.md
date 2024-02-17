## Telekit

A Telegram automation client built with Python's Telethon library. Currently supports:

1. Automatically transcribing your own voice messages.
2. Using shortcut to transcribe other people's voice messages.

### Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)

### Installation

#### Prerequisites

- Python 3.x
- pip
- Telegram account
- OpenAI account
- Telegram API ID and hash: https://core.telegram.org/api/obtaining_api_id

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/doomuch/telekit telekit
   ```
2. Navigate to the project directory:
   ```bash
   cd telekit
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy an `.env` file and add your keys there:
   ```bash
   cp .env.example .env
   ```

### Usage

#### From Commandline

To add a client with a specific session name:

```bash
python app.py add-client my_session
```

To delete a client:

```bash
python app.py delete-client
```

To start the program:

```bash
python app.py start-program
```

#### From Docker

To run docker container:

```bash
sudo docker run -d -p 4000:80 --env-file .env -v ./data:/app/data -v ./data/sessions:/app/data/sessions --name telekit telekit
```

It runs `start-program` command on startup so if you already has a session, you don't need to run `start-program` again.

To init a new session (replace {SESSION_NAME} with your session name):

```bash
sudo docker exec telekit python /app/app.py add-client {SESSION_NAME}
```

After that you need to run `start-program` and proceed Telegram authentication:

```bash
sudo docker exec -it telekit python /app/app.py add-client session
```

After entering the necessary information interactively, you can exit the interactive session without stopping the Python script by pressing `Ctrl + P` or `Ctrl + Q`. This key combination detaches from the container without terminating the running process.

### Features

- Transcribes voice messages.
- Handles multiple clients.
- Supports various output formats.

### Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

This project is in early development stage, so there are many things to be done. Feel free to open an issue to discuss what you would like to change.
