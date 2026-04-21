from .keywords import ADMISSION_PRIORITY_KEYWORDS
from .utils import contains_any


def is_admission_query(text: str) -> bool:
    return contains_any(text, ADMISSION_PRIORITY_KEYWORDS)
