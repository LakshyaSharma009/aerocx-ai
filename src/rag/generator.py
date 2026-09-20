"""Grounded answer generator with a provider abstraction.

Providers (selected via LLM_PROVIDER env var):
  - mock: deterministic template answer built strictly from retrieved context.
  - openai: Chat Completions API (requires LLM_API_KEY; lazy import).
  - huggingface: local text2text/QA pipeline (lazy import).

Grounding rules enforced in every provider's system prompt AND in the mock path:
  - answer only from supplied context; say when info is unavailable;
  - never invent technical facts; cite source document names;
  - distinguish recommendations from factual information.
"""

from __future__ import annotations

from src.utils.config import get_settings

SYSTEM_RULES = """You are AeroCX AI, an aviation customer-support assistant.
STRICT RULES:
1. Answer ONLY using the supplied context. If the context lacks the answer, say: "I don't have that information in the provided documents."
2. Do NOT invent technical facts, part numbers, limits, or procedures.
3. Cite source document names for every factual claim, e.g. [maintenance_delay_policy.md].
4. Clearly separate FACT (from context) from RECOMMENDATION (your suggestion).
5. Keep the answer concise and actionable for a support agent."""


ABSTAIN_MESSAGE = ("I don't have sufficiently relevant information in the AeroCX "
                   "knowledge base to answer this question. No retrieved passage met "
                   "the relevance threshold, so I cannot give a grounded answer. "
                   "RECOMMENDATION: route this query to a human specialist.")


def abstain_response() -> dict:
    """Canonical abstention: no sources, no provider call, no recommendation content."""
    return {"answer": ABSTAIN_MESSAGE, "sources": [], "provider": "abstention"}


def _mock_answer(query: str, contexts: list[dict]) -> str:
    if not contexts:
        return ("I don't have that information in the provided documents. "
                "No relevant passages were retrieved. RECOMMENDATION: route to a human specialist.")
    facts = "\n".join(f"- {c['text'][:280]}... [{c['doc_name']}]" for c in contexts[:3])
    srcs = ", ".join(sorted({c['doc_name'] for c in contexts[:3]}))
    return (f"FACT — based on the retrieved context for: '{query}':\n{facts}\n"
            f"RECOMMENDATION: follow the cited procedure and confirm MEL/contract implications "
            f"with the duty owner.\nSources: {srcs}")


def _openai_answer(query: str, contexts: list[dict], model: str, api_key: str) -> str:
    from openai import OpenAI  # lazy

    client = OpenAI(api_key=api_key)
    ctx = "\n\n".join(f"[{c['doc_name']}] {c['text']}" for c in contexts)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_RULES},
                  {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {query}"}],
        temperature=0.1, max_tokens=500)
    return str(resp.choices[0].message.content)


def _hf_answer(query: str, contexts: list[dict], model: str) -> str:
    from transformers import pipeline  # lazy

    qa = pipeline("question-answering", model=model)
    if not contexts:
        return "I don't have that information in the provided documents."
    best, best_score = None, -1.0
    for c in contexts:
        try:
            r = qa(question=query, context=c["text"][:2000])
            if float(r["score"]) > best_score:
                best, best_score = r, float(r["score"])
        except Exception:
            continue
    if best is None:
        return _mock_answer(query, contexts)
    srcs = ", ".join(sorted({c["doc_name"] for c in contexts[:3]}))
    return (f"FACT: {best['answer']} (confidence {best_score:.2f}, from retrieved context).\n"
            f"RECOMMENDATION: verify against the full procedure before acting.\nSources: {srcs}")


def generate(query: str, contexts: list[dict]) -> dict:
    """Generate a grounded answer. Returns {answer, sources, provider}.

    Safety net: contexts scoring below RAG_MIN_SIMILARITY are treated as
    ungrounded and abstained WITHOUT invoking any LLM provider. (Primary
    gating happens in Retriever.search_gated + the API/analysis call sites,
    which skip generate() entirely; this covers direct callers.)
    """
    s = get_settings()
    if contexts and all(isinstance(c, dict) and "score" in c for c in contexts):
        if max(float(c["score"]) for c in contexts) < s.rag_min_similarity:
            return abstain_response()
    provider = (s.llm_provider or "mock").lower()
    sources = sorted({c["doc_name"] for c in contexts})
    try:
        if provider == "openai" and s.llm_api_key:
            return {"answer": _openai_answer(query, contexts, s.llm_model, s.llm_api_key),
                    "sources": sources, "provider": "openai"}
        if provider == "huggingface":
            return {"answer": _hf_answer(query, contexts, s.llm_model),
                    "sources": sources, "provider": "huggingface"}
    except Exception as e:  # fall through to mock rather than failing the request
        return {"answer": _mock_answer(query, contexts) + f"\n(Note: {provider} provider failed: {e})",
                "sources": sources, "provider": "mock-fallback"}
    return {"answer": _mock_answer(query, contexts), "sources": sources, "provider": "mock"}
