from pathlib import Path

from core.config import DEFAULT_PATH, load_config


def test_defaults_from_file() -> None:
    cfg = load_config(env={})
    assert cfg.llm.context_tokens == 8192
    assert cfg.embed.model == "bge-m3"
    assert cfg.data_dir == Path("data")


def test_env_overrides_keep_types() -> None:
    cfg = load_config(DEFAULT_PATH, env={"TTR_LLM_MODEL": "gemma4:12b", "TTR_SEARCH_TOP_K": "5"})
    assert cfg.llm.model == "gemma4:12b"
    assert cfg.search.top_k == 5
