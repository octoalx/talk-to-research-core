from core.embed import FakeEmbedder
from core.llm import ChatMessage, FakeChatModel


def test_fake_embedder_is_deterministic_and_normalised() -> None:
    emb = FakeEmbedder(dim=16)
    a, b, c = emb.embed(["пеня", "пеня", "неустойка"])
    assert a == b
    assert a != c
    assert abs(sum(x * x for x in a) - 1.0) < 1e-9


def test_fake_chat_model_records_calls() -> None:
    model = FakeChatModel(lambda messages: "не нашёл в документах")
    out = model.complete([ChatMessage("user", "Какая неустойка у Медиа Плюс?")])
    assert out == "не нашёл в документах"
    assert len(model.calls) == 1
    assert "".join(model.stream([ChatMessage("user", "x")])).replace(" ", "") != ""
