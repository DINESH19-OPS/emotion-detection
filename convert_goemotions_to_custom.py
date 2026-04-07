import argparse
import csv
import re
from collections import Counter
from pathlib import Path


TARGET_LABELS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "love",
    "surprise",
    "neutral",
    "fraustation",
    "confusion",
    "boredom",
    "intrest",
    "anxiety",
]

PRIORITY = [
    "anxiety",
    "fraustation",
    "confusion",
    "boredom",
    "intrest",
    "fear",
    "anger",
    "sadness",
    "love",
    "joy",
    "surprise",
    "neutral",
]

GOEMOTION_TO_TARGET = {
    "admiration": "love",
    "amusement": "joy",
    "anger": "anger",
    "annoyance": "fraustation",
    "approval": "joy",
    "caring": "love",
    "confusion": "confusion",
    "curiosity": "intrest",
    "desire": "intrest",
    "disappointment": "sadness",
    "disapproval": "fraustation",
    "disgust": "fraustation",
    "embarrassment": "anxiety",
    "excitement": "joy",
    "fear": "fear",
    "gratitude": "joy",
    "grief": "sadness",
    "joy": "joy",
    "love": "love",
    "nervousness": "anxiety",
    "optimism": "joy",
    "pride": "joy",
    "realization": "surprise",
    "relief": "joy",
    "remorse": "sadness",
    "sadness": "sadness",
    "surprise": "surprise",
    "neutral": "neutral",
}

BOREDOM_PATTERN = re.compile(r"\b(bored|boring|dull|tedious|uninterested|nothing to do|monotonous|sleepy)\b", re.IGNORECASE)


def pick_label(text: str, mapped_labels: set[str]) -> str:
    if BOREDOM_PATTERN.search(text):
        return "boredom"

    for label in PRIORITY:
        if label in mapped_labels:
            return label

    return "neutral"


def convert_split(input_file: Path, output_file: Path, emotions: list[str]) -> Counter:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()

    with input_file.open("r", encoding="utf-8") as source, output_file.open("w", encoding="utf-8", newline="") as target:
        reader = csv.reader(source, delimiter="\t")
        writer = csv.writer(target, delimiter=";", lineterminator="\n")

        for row in reader:
            if len(row) < 2:
                continue

            text = row[0].strip()
            raw_indices = row[1].strip()
            if not text or not raw_indices:
                continue

            labels = []
            for index_text in raw_indices.split(","):
                index_text = index_text.strip()
                if not index_text.isdigit():
                    continue
                idx = int(index_text)
                if idx < 0 or idx >= len(emotions):
                    continue
                labels.append(emotions[idx])

            mapped = {GOEMOTION_TO_TARGET[label] for label in labels if label in GOEMOTION_TO_TARGET}
            final_label = pick_label(text, mapped)
            writer.writerow([text, final_label])
            counts[final_label] += 1

    return counts


def print_summary(name: str, counts: Counter) -> None:
    total = sum(counts.values())
    print(f"\n{name} -> {total} rows")
    for label in TARGET_LABELS:
        print(f"  {label:12s} {counts.get(label, 0)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert GoEmotions TSV files to single-label custom semicolon files.")
    parser.add_argument("--data-dir", default="data", help="Folder containing train.tsv/dev.tsv/test.tsv and emotions.txt")
    parser.add_argument("--out-dir", default="data/custom_mapped", help="Output folder for converted files")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)

    emotions_path = data_dir / "emotions.txt"
    emotions = [line.strip() for line in emotions_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    train_counts = convert_split(data_dir / "train.tsv", out_dir / "train_custom.txt", emotions)
    val_counts = convert_split(data_dir / "dev.tsv", out_dir / "val_custom.txt", emotions)
    test_counts = convert_split(data_dir / "test.tsv", out_dir / "test_custom.txt", emotions)

    print_summary("train_custom.txt", train_counts)
    print_summary("val_custom.txt", val_counts)
    print_summary("test_custom.txt", test_counts)


if __name__ == "__main__":
    main()
