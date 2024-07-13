FROM python:3.10.14

COPY . /app
WORKDIR /app

RUN (pip3 install -r requirements.txt)

EXPOSE 8002
CMD ["python3", "main.py"]