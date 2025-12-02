Script for **automatic** receipt of **daily rewards** on <a href="https://pixai.art">PixAI</a>.

## 🚀 Quick Start

Clone the repository, set up environment variables and run using docker:
```bash
# Clone repository
git clone https://github.com/assailance/pixai-daily-rewards
cd pixai-daily-rewards

# Run docker (pre-configure environment variables
# to specify USE_DOCKER_SELENIUM=True and SELENIUM_REMOTE_URL)
docker compose run --rm pixai && docker compose logs -f -t
```

## Running without docker

1. Download **chrome** (binary) and **chromedriver** of the required version
2. Install **dependencies**:
```bash
# Using pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or using uv
uv sync
```
3. Set **environment variables**:
```bash
# Create .env file
mv .env.template .env
```
```env
# .env
...
USE_DOCKER_SELENIUM=False
CHROMEDRIVER_PATH=<path-to-chrome>
CHROMEBINARY_PATH=<path-to-chromedriver>
```
4. **Run** the script:
```bash
# Using python
python main.py

# Or using uv
uv run main.py
```

## 📆 Running with cron

Set your preferred script **schedule** and **logging** using crontab:
1. Install **cron**:
```bash
sudo apt install cron
```
2. Create a periodic **task**:
```bash
# Open the editor
crontab -e

# Insert run command
# Set the execution time and file path
30 16 * * * cd /opt/pixai-daily-rewards && venv/bin/python main.py >> main.log 2>&1
```
