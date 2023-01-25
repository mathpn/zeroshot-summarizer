This app will use FastAPI for API calls. In the backend, RabbitMQ will distribute inference steps across workers and we'll use Redis to store the results.

docker run --rm -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=my_user -e RABBITMQ_DEFAULT_PASS=my_password rabbitmq:3.10-management

docker run --rm -p 6379:6379 redis:latest
