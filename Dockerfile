FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# create non-root user
RUN useradd -m appuser

# switch to non-root user
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]