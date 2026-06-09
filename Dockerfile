FROM python:3.11-slim
LABEL authors="sasha"

WORKDIR /app

COPY main/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY    main/ .

CMD ["python", "app.py"]