# zeroshot-summarizer-v1

The goal of this project is to finetune a T5 transformer to take abstracts and return titles. Not only that, but the generated title should be costumizable according to some predefined adjectives.

There will be an API (FastAPI) to receive inference requests, which will be added to a RabbitMQ queue. An inference worker will consume this queue and store results in a Redis instance.

# Running in development mode (mounted source files)

```bash
docker-compose -f docker-compose-local.yml up
```

# Building and running

```bash
docker-compose rm && docker-compose -f docker-compose.yml up --build -d && docker-compose logs --tail 100 -f
```
