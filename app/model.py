"""
Inference functions for fine-tuned T5 model inference.
"""

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration


def create_inference(model, tokenizer):
    def inference(
        sequence: str,
        descriptors: list[str],
        max_length: int = 20,
        temperature: float = 1.0,
        sample: bool = True,
    ):
        desc_str = ", ".join(descriptors)
        sequence = f"summarize {desc_str}: {sequence.strip().lower()}"
        input_ids = tokenizer(sequence, return_tensors="pt").input_ids
        outputs = model.generate(
            input_ids,
            temperature=temperature,
            do_sample=sample,
            max_length=max_length,
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    return inference


if __name__ == "__main__":
    tokenizer = T5Tokenizer.from_pretrained("t5-small", model_max_length=512)
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    # model.load_state_dict(torch.load("./t5_small_ft_22.pth", map_location="cpu"))

    inference = create_inference(model, tokenizer)
    out = inference(
        # "attention is all you need" paper
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.",
        ["answer", "complex", "abstract"],
        20,
        temperature=0.5,
    )
    print(out)
