FROM python:3.10-slim-buster

WORKDIR /app

COPY src/ /app/src

COPY requirements.txt /app/requirements.txt 

RUN pip install -r requirements.txt 

CMD ["python src/app.py"]