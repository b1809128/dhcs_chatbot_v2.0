from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = DATA_DIR / "index"
OLLAMA_URL = "http://172.20.10.6:11434/api/generate"# Update with your ip address and port
MODEL_NAME = "qwen2:1.5b"  # Update with your model name
