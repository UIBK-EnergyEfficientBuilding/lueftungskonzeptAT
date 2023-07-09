FROM python:3.11-alpine as builder

COPY . /app/
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m venv /opt/venv
RUN pip install --no-cache-dir /app/
RUN pip install --no-cache-dir gunicorn

FROM python:3.11-alpine
RUN addgroup --system app && adduser -S -G app app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "lueftungstool:app"]
