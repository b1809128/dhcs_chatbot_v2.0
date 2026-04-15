from typing import List, Optional

from .admission_context import build_admission_context
from .document_context import build_document_context
from .library_context import build_library_context
from .schedule_context import build_schedule_context
from .study_material_context import build_study_material_context
from .types import ContextBuilder, StructuredContext
from .utils import format_context_data


def build_context(query: str) -> Optional[str]:
    normalized_query = query.lower().strip()

    if schedule_result := build_schedule_context(normalized_query):
        return format_context_data(schedule_result)

    if admission_result := build_admission_context(normalized_query):
        return format_context_data(admission_result)

    builders: List[ContextBuilder] = [
        build_document_context,
        build_study_material_context,
        build_library_context,
    ]

    context_parts = [
        format_context_data(result)
        for builder in builders
        if (result := builder(normalized_query))
    ]

    if not context_parts:
        return None

    return "\n\n".join(context_parts)


def build_direct_context(query: str) -> Optional[StructuredContext]:
    normalized_query = query.lower().strip()

    builders: List[ContextBuilder] = [
        build_schedule_context,
        build_admission_context,
        build_document_context,
        build_library_context,
        build_study_material_context,
    ]

    for builder in builders:
        result = builder(normalized_query)
        if result:
            return result

    return None
