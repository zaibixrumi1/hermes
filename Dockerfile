FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install Hermes CLI
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 2. Add Hermes to PATH
ENV PATH="/root/.hermes/bin:/root/.local/bin:${PATH}"

# 3. Install the external DB memory plugin
RUN hermes plugins install severian || true

# 4. Tell Hermes to use the external DB
ENV HERMES_MEMORY_PROVIDER="severian"

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your bot code
COPY bot.py .

# 7. Start the bot
CMD ["python", "bot.py"]
