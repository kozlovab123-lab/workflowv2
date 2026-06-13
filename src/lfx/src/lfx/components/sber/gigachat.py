from pydantic.v1 import SecretStr

from lfx.base.models.gigachat_constants import GIGACHAT_MODELS
from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.io import DropdownInput, FloatInput, IntInput, SecretStrInput, SliderInput


class GigaChatModelComponent(LCModelComponent):
    display_name: str = "GigaChat"
    description: str = "Generate text using Sber GigaChat."
    icon = "Sber"
    name = "GigaChatModel"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        SecretStrInput(
            name="credentials",
            display_name="GigaChat credentials",
            info="Authorization key from developers.sber.ru (GigaChat API).",
            real_time_refresh=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model",
            info="GigaChat model name.",
            options=GIGACHAT_MODELS,
            value=GIGACHAT_MODELS[0],
            combobox=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            info="Sampling temperature.",
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max tokens",
            info="Maximum number of tokens to generate.",
            advanced=True,
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        try:
            from langchain_gigachat.chat_models import GigaChat
        except ImportError as e:
            msg = (
                "langchain-gigachat is not installed. "
                "Install with: uv pip install langchain-gigachat"
            )
            raise ImportError(msg) from e

        from lfx.base.models.unified_models.credentials import ensure_decrypted_credential

        raw_credentials = SecretStr(self.credentials).get_secret_value() if self.credentials else None
        credentials = ensure_decrypted_credential(raw_credentials)
        return GigaChat(
            credentials=credentials,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens or None,
            verify_ssl_certs=False,
            streaming=self.stream,
        )
