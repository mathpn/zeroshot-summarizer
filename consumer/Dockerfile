FROM python:3.11

WORKDIR /home/

COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait

ADD consumer/requirements.txt requirements.txt
ADD consumer ./consumer
ADD src ./src

RUN chmod +x ./consumer/start.sh
RUN apt-get update && apt-get -y install gcc cmake git pkg-config
RUN pip install -r requirements.txt
RUN pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

EXPOSE 8000/tcp