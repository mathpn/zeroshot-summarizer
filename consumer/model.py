"""
Inference functions for fine-tuned T5 model inference.
"""

from typing import Any, NamedTuple

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer


class InferenceQuery(NamedTuple):
    inference_id: str
    headers: dict
    sequence: str


class InferenceResult(NamedTuple):
    inference_id: str
    headers: dict
    result: str


def build_query(headers: dict[str, Any], body: dict[str, str]) -> InferenceQuery:
    inference_id = headers["inference_id"]
    descriptors = ", ".join(body["descriptors"])
    return InferenceQuery(inference_id, headers, f"summarize {descriptors}: {body['sequence']}")


def create_inference(model, tokenizer):
    model = model.eval()

    def inference(
        queries: list[InferenceQuery],
        sample: bool = True,
    ) -> list[InferenceResult]:
        sequences = [query.sequence for query in queries]
        input_ids = tokenizer(sequences, return_tensors="pt").input_ids
        outputs = model.generate(input_ids, do_sample=sample)
        outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        print(f"------------> {outputs = }")
        return [InferenceResult(query.inference_id, query.headers, outputs[i]) for i, query in enumerate(queries)]

    return inference


if __name__ == "__main__":
    tokenizer = T5Tokenizer.from_pretrained("t5-small", model_max_length=512)
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    model.load_state_dict(torch.load("./models/t5_small_ft_22.pth", map_location="cpu"))

    inference = create_inference(model, tokenizer)
    query = InferenceQuery(
        "foobar",
        "summarize answer, complex, concrete: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data."
    )
    out = inference([query])
    print(out)
