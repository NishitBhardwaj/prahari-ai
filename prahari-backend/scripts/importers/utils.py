import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'dataset-generator' / 'output'
CSV_DIR = BASE_DIR / 'csv'
JSON_DIR = BASE_DIR / 'json'

def get_csv_path(filename: str) -> Path:
    return CSV_DIR / filename

def print_progress(step: int, total: int, title: str):
    print(f'\n[{step}/{total}] {title}...')

def print_success(message: str):
    print(f'\x1b[32m✓\x1b[0m {message}')
