import json
import random

def split_jsonl_file(file_path, train_ratio=0.7):
    # Einlesen der Datei
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Zufälliges Mischen der Zeilen
    random.shuffle(lines)

    # Berechnung der Anzahl der Zeilen für das Training
    train_size = int(len(lines) * train_ratio)

    # Aufteilung der Daten
    train_lines = lines[:train_size]
    test_lines = lines[train_size:]

    # Speichern der Trainingsdaten
    with open('training_ft.jsonl', 'w', encoding='utf-8') as train_file:
        for line in train_lines:
            train_file.write(line)

    # Speichern der Testdaten
    with open('test_ft.jsonl', 'w', encoding='utf-8') as test_file:
        for line in test_lines:
            test_file.write(line)

file_path = 'Repo/ChatGPT-Finetuning/data_finetuning.jsonl' 
split_jsonl_file(file_path)
