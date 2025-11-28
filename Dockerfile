# pull official base image
FROM python:3.12-slim

# install system dependencies
RUN apt-get update && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /opt/pixai-daily-rewards

# set python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# run the script
CMD ["python", "main.py"]
