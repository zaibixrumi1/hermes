FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl bash git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
ENV PATH="/root/.hermes/bin:/root/.local/bin:${PATH}"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
