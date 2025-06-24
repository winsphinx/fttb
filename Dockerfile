FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir uv && \
    uv sync --no-cache

EXPOSE 5000

ENTRYPOINT ["uv", "run", "main.py"]
