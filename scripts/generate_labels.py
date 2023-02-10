"""
Use a zero-shot classifier to classify the titles according to some labels.

It's limited to "only" 100_000 samples due to limited resources.
Ideally, the entire dataset should be used.
"""

import json
import random
import time
import zipfile

import torch
from torch.utils.data import DataLoader
from transformers import pipeline


def main():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print("loading bart-large-mnli")
    classifier = pipeline(
        "zero-shot-classification", model="facebook/bart-large-mnli", device=device
    )

    arxiv_data = []
    archive = zipfile.ZipFile("arxiv_dataset.zip", "r")
    for line in archive.open("arxiv-metadata-oai-snapshot.json"):
        line = json.loads(line)
        arxiv_data.append((line["title"].lower(), line["abstract"].lower()))

    random.seed(42)
    arxiv_data = random.sample(arxiv_data, 100_000)

    candidate_labels = [
        ["inquiry", "answer"],
        ["simple", "complex"],
        ["abstract", "concrete"],
    ]

    loader = DataLoader(arxiv_data, batch_size=256)
    labels = []
    init = time.time()
    for i, (title, _) in enumerate(loader):
        if i % 1 == 0:
            print(f"{i}/{len(loader)} processed in {time.time() - init:.2f}")
            init = time.time()
        ll = []
        for candidates in candidate_labels:
            with torch.no_grad():
                result = classifier(list(title), candidates)
                ll.extend(x["labels"][0] for x in result)
        labels.append(ll)
    with open("labels.json", "w") as out:
        json.dump(labels, out)
    print("saved labels to labels.json")


if __name__ == "__main__":
    main()
