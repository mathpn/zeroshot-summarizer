FROM python:3.11

WORKDIR /home/

COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait

ADD app/requirements.txt requirements.txt
ADD app ./app
ADD src ./src

RUN chmod +x ./app/start.sh
RUN chmod +x ./app/start_dev.sh
RUN pip install -r requirements.txt

EXPOSE 8000/tcp