FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system appuser \
    && adduser --system --ingroup appuser appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY tests ./tests
COPY plugins ./plugins
COPY main.py ./

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]
