FROM python:3.11

WORKDIR /home/

ADD requirements.txt requirements.txt
ADD app ./app
ADD src ./src

RUN chmod +x ./app/start.sh
RUN apt-get update && apt-get -y install gcc cmake git pkg-config
RUN pip install -r requirements.txt
RUN pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

EXPOSE 8000/tcp