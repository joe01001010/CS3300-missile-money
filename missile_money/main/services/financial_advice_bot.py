# missile_money/main/services/financial_advice_bot.py
import os
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from llama_cpp import Llama


_MODEL_NAME_FALLBACKS = [
    os.getenv("FIN_BOT_MODEL_FILENAME"),
    "FinancialAdvice-Qwen2.5-7B.Q4_K_M.gguf",
    "FinancialAdvice-Qwen2.5-7B.F16.gguf",
]
MODEL_CANDIDATE_NAMES = [name for name in _MODEL_NAME_FALLBACKS if name]
SYSTEM_PROMPT = (
    "You are Missile Money, an educational personal-finance coach. "
    "Offer actionable budgeting, saving, or debt-management tips, note you aren't a licensed advisor, "
    "and decline requests for legal or guaranteed investment outcomes."
)


@lru_cache
def _model() -> Llama:
    base_dir = Path(settings.BASE_DIR)
    search_paths = []
    for filename in MODEL_CANDIDATE_NAMES:
        search_paths.extend(
            [
                base_dir / "models" / filename,
                base_dir.parent / "models" / filename,
            ]
        )

    existing_paths = [path for path in search_paths if path.exists()]

    if not existing_paths:
        raise FileNotFoundError(
            "Financial advice model file not found. Checked: "
            + ", ".join(str(path) for path in search_paths)
        )

    last_error: ValueError | None = None
    for model_path in existing_paths:
        try:
            return Llama(
                model_path=str(model_path),
                n_ctx=int(os.getenv("FIN_BOT_CTX", 4096)),
                n_threads=int(os.getenv("FIN_BOT_THREADS", os.cpu_count() or 4)),
                n_gpu_layers=int(os.getenv("FIN_BOT_GPU_LAYERS", 0)),
                verbose=False,
            )
        except ValueError as exc:
            last_error = exc
            continue

    raise RuntimeError(
        "Unable to load any available financial advice model. "
        "This usually means the GGUF quantization is too large for the machine's available memory. "
        "Tried: " + ", ".join(str(path) for path in existing_paths)
    ) from last_error


def generate_financial_advice(prompt: str, history: list[dict[str, str]]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": prompt}]
    completion = _model().create_chat_completion(
        messages=messages,
        temperature=0.4,
        top_p=0.9,
        max_tokens=512,
    )
    return completion["choices"][0]["message"]["content"].strip()
