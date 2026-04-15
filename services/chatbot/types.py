from typing import Any, Callable, Dict, Optional

JsonDict = Dict[str, Any]
StructuredContext = Dict[str, Any]
ContextBuilder = Callable[[str], Optional[StructuredContext]]
