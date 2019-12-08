FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements/base.txt /code/
RUN pip install -r base.txt
COPY . /code/