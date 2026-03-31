# 1. Base image
FROM python:3.12-slim

# 2. Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Clone repo (public repo)
RUN git clone https://github.com/niveshkr32/Moving-Average-Crossover-Strategy.git .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Set environment variables (optional)
ENV TELEGRAM_TOKEN=8652752416:AAHRHdMM5FCaSfKXKtFCnmmcIwLzYwpalpc
ENV TELEGRAM_CHAT_ID=1517706156

# 7. Command to run
CMD ["python", "strategy_3.py"]
