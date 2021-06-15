FROM python:3.7

ADD . /opt

WORKDIR /opt

RUN pip install -r requirements.txt

CMD python3 app.py
