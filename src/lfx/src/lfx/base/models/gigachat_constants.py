from .model_metadata import create_model_metadata

GIGACHAT_MODELS = [
    "GigaChat",
    "GigaChat-2",
    "GigaChat-2-Max",
    "GigaChat-2-Pro",
    "GigaChat-Max",
    "GigaChat-Plus",
    "GigaChat-Pro",
]

GIGACHAT_MODELS_DETAILED = [
    create_model_metadata(
        provider="SBER",
        name=model,
        icon="Sber",
        tool_calling=model in {"GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max", "GigaChat-Pro", "GigaChat-Max"},
        default=model == "GigaChat",
    )
    for model in GIGACHAT_MODELS
]
