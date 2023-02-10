"""
Launch Gradio demo with the model.
"""

import gradio as gr
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

from app.model import create_inference

tokenizer = T5Tokenizer.from_pretrained("t5-small", model_max_length=512)
model = T5ForConditionalGeneration.from_pretrained("t5-small")
model.load_state_dict(torch.load("./models/t5_small_ft_22.pth", map_location="cpu"))
inference = create_inference(model, tokenizer)


def summarize(
    abstract: str,
    answerness: str,
    complexity: str,
    concreteness: str,
    temperature: float = 0.1,
    max_len: int = 20,
):
    descriptors = [answerness, complexity, concreteness]
    return inference(abstract, descriptors, max_len, temperature)


if __name__ == "__main__":
    inputs = [
        "text",
        gr.Radio(["inquiry", "answer"]),
        gr.Radio(["simple", "complex"]),
        gr.Radio(["abstract", "concrete"]),
        gr.Slider(0.01, 1, value=0.2),
        gr.Slider(5, 100, value=20, step=1),
    ]

    outputs = gr.Text(label="summary")
    demo = gr.Interface(fn=summarize, inputs=inputs, outputs=outputs, title="Zeroshot Summarizer")
    demo.launch()
