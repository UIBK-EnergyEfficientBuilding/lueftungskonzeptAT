FROM python:3.11-slim as builder

COPY . /app/
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m venv /opt/venv
RUN pip install --no-cache-dir /app/
RUN pip install --no-cache-dir gunicorn

FROM python:3.11-slim
RUN useradd -r -U app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_CMD_ARGS="--access-logfile - --error-logfile -"

USER app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "lueftungstool:create_app()"]
