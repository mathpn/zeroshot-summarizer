import asyncio
import time

import aiohttp

BODY = {
    "sequence": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.",
    "descriptors": ["answer", "complex", "concrete"],
}


async def request():
    async with aiohttp.ClientSession() as session:
        init = time.perf_counter()
        async with session.post("http://localhost:8383/summarize", json=BODY) as resp:
            assert resp.status == 200
        end = time.perf_counter()
        print(f"request took {1000 * (end - init):.2f} ms")


async def main():
    tasks = set()
    for _ in range(100):
        task = asyncio.create_task(request())
        task.add_done_callback(tasks.discard)
        tasks.add(task)
        await asyncio.sleep(0.1)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
