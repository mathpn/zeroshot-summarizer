# Zeroshot Summarizer

Zeroshot summarizer is a service that takes *abstracts* and some predefined *adjectives* as inputs and *return titles* summarized according to those adjectives. This is done using a finetuned T5 transformer model. This projects uses FastAPI, Pytorch, 🤗 transformers, Apache Kafka and RabbitMQ. Dynamic batching is used to improve efficiency.

## Sample request and result

Request with the _"Attention is all you need"_ paper abstract:

```json
{
    "sequence": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.",
    "descriptors": [
        "answer",
        "complex",
        "concrete"
    ]
}
```

Response:

```json
{
  "summary": "the Transformer: new parallel neural networks based on attention for coherent encoder-decoder generation"
}
```

Changing the descriptors to _answer, simple, abstract_ yields:

```json
{
  "summary": "the Transformer: a novel simple network architecture for sequencing"
}
```


## How the model was finetuned

1. Generating training data

    The [arxiv dataset](https://www.kaggle.com/datasets/Cornell-University/arxiv) from Kaggle was used as a source of title-summary pairs. It is - of course - heavily biased towards STEM fields and therefore the model is not expected to generalize well to other styles and areas of knowledge. Besides these pairs, we also need to label the titles according to those predefined adjectives.

    This was done using a [zero-shot text classifier model](https://huggingface.co/facebook/bart-large-mnli). In theory, many more adjective pairs could be generated. It is even theoretically possible to zero-shot-label without defining mutually exclusive pairs of characteristics. Still, the simple path was taken here due to computational constraints. These were the predefined adjective pairs:

    ```json
    [
        ["inquiry", "answer"],
        ["simple", "complex"],
        ["abstract", "concrete"]
    ]
    ```
2. Finetuning the T5 transformer

    T5ForConditionalGeneration from the 🤗 [transformers](https://pypi.org/project/transformers/) package was used as a foundational model. It was finetuned with prompts of the following format:

    > summarize answer, simple, concrete: I am a very short abstract.

    and the title was the expected output.

    The model was finetuned for 22 epochs on a subset of the arxiv dataset. For details check the train.ipynb file.


## How the service works

The service consists of two main parts: the app and the consumer. They rely on Apacha Kafka and RabbitMQ. The project is Dockerized using docker-compose.

1. The app

    It is the API itself, which has a single summarize endpoint (besides a health endpoint). It's very simple and built using FastAPI. Although FastAPI is great, as its own documentation suggests, it's not well suited for CPU-heavy tasks, even less so for multithreaded works (even though uvicorn can spawn multiple workers, which is something else entirely). Thus, requests are inserted in an inference queue, which is an Apache Kafka topic. The consumer does the inference step and writes the result to a short-lived RabbitMQ queue. Meanwhile, the app asynchronously awaits for the result to arrive to the queue, thus freeing the app to handle new requests.

2. The consumer

    It consists of a Kafka Consumer and a RabbitMQ Publisher. Those two are bundled together and launched as a thread. Since Pytorch internal functions aren't constrained by the [GIL](https://wiki.python.org/moin/GlobalInterpreterLock), launching more threads will speed up inference up to a certain hardware limit.

    Still, it's expensive to call an inference function for every request and large models are optimized for batched inference. That's why **dynamic batching** was implemented. Basically, the Kafka Consumers consumes up to 32 (arbitraty number) requests at once (if available). Thus, when load is low, usually each request is processed individually. But then load is high, requests will be grouped in batches of up to 32 items for inference. Dynamic batching improves efficiency and allows the same server to handle more requests per unit of time.

    Finally, each result is published to its own short-lived RabbitMQ queue.


## Running the service

### Running in development mode (mounted source files)

```bash
docker-compose -f docker-compose-local.yml up
```

### Rebuilding the Docker images (development mode)

```bash
docker-compose rm && docker-compose -f docker-compose-local.yml up --build
```

### Building and running (production mode)

```bash
docker-compose rm && docker-compose up --build
```

### Running (production mode)

```bash
docker-compose up
```
