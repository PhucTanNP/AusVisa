from __future__ import annotations
from config import GEMINI_MODEL


# Single place to configure your Gemini chat model
def get_chat(model: str | None = None, temperature: float = 0):
    """_summary_

    Args:
        model (str | None, optional): _description_. Defaults to None.
        temperature (float, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    try:
        # Import here to avoid import-time errors if the installed Google GenAI
        # integration package has an incompatible API (e.g. GenerationConfig.Modality).
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model or GEMINI_MODEL, temperature=temperature)
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        # Provide a clearer error message to help with dependency fixes.
        msg = (
            "Failed to initialize Google Generative AI chat backend. "
            "This often means the installed 'langchain_google_genai' or 'google-generativeai' "
            "package version is incompatible. Original error: "
            f"{exc!r}.\n\n"
            "Possible fixes:\n"
            "  - Pin compatible versions in requirements.txt (e.g. google-generativeai and langchain_google_genai)\n"
            "  - Or switch to a different LLM backend in llm/client.py\n"
        )
        raise RuntimeError(msg) from exc