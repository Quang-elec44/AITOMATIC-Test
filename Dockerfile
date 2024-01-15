FROM python:3.10-slim-buster

WORKDIR /app

COPY src/ /app/src/

COPY requirement.txt /app/requirement.txt 

RUN pip install -r requirement.txt 

CMD ["python src/app.py"]