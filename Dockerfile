FROM python:3.8
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-dev build-essential -y
RUN apt-get install libpq-dev
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
WORKDIR /app
COPY . .
RUN pip install -r requeriments.txt

