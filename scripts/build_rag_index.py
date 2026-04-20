from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.chatbot.rag_service import load_rag_index  # noqa: E402


def main() -> None:
    index = load_rag_index()
    print(
        f"Da build xong RAG index local voi {len(index['documents'])} documents."
    )


if __name__ == "__main__":
    main()
