FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://pypi.org/simple -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
