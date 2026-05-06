FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal. Cloud Run sets PORT.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

COPY mcp_server/requirements.txt /app/mcp_server/requirements.txt
RUN pip install --no-cache-dir -r /app/mcp_server/requirements.txt

COPY mcp_server /app/mcp_server
COPY data /app/data

EXPOSE 8080

# Cloud Run injects PORT; respect it.
CMD ["python", "-m", "mcp_server.server"]
