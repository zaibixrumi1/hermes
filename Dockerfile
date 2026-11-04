FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    bash \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Hermes CLI
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
ENV PATH="/root/.hermes/bin:/root/.local/bin:${PATH}"

# Install memory plugin
RUN hermes plugins install severian || true
ENV HERMES_MEMORY_PROVIDER="severian"

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY bot.py .
COPY pinger.py .

# Start the pinger in the background, then start the bot
CMD ["sh", "-c", "python pinger.py & python bot.py"]
