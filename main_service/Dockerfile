FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5003", "main_service:app"]

FROM python:3.9

# MySQL 클라이언트 설치를 위한 의존성 추가
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["gunicorn", "--bind", "0.0.0.0:5002", "festival_service:create_app()"]

