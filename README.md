Matrix bot

## Installation

1. Clone the repository
```bash
git clone https://github.com/KERELKO/matrix_bot
cd matrix_box
```
2. Fill the environment variables
```bash
cp .env.template > .env
```
__Required variables are:__
```bash
MATRIX_HOMESERVER_URL
MATRIX_BOT_USERNAME
MATRIX_BOT_PASSWORD
```

3. Run in Docker
```bash
docker build -t matrix_bot .
docker run matrix_bot
```
4. Check for logs
```bash
docker logs matrix_bot
```
