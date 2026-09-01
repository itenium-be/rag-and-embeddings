import logging

from rag.models import Check, Chunk, Config, Citation, Result, Scored
from web.trace import format_critique, format_question, format_result, install_console_logging


def _scored(cid: str, title: str, ranks: dict) -> Scored:
    chunk = Chunk(id=cid, text="t", source="s", source_type="cv", title=title, location="p.2")
    return Scored(chunk=chunk, score=0.5, ranks=ranks)


def _result(**overrides) -> Result:
    used = [_scored("a", "Bram Willems", {"dense": 3, "bm25": 1, "fused": 1, "rerank": 1})]
    defaults = dict(
        question="Ik wil AZ-900 halen",
        rewritten=None,
        candidates=used + [_scored("b", "Dries", {"bm25": 2, "fused": 2})],
        used=used,
        answer="An answer [1].",
        citations=[],
    )
    return Result(**{**defaults, **overrides})


def test_question_line_names_the_step_and_the_question():
    line = format_question("Ik wil AZ-900 halen", 2, Config(bm25=True))
    assert "step 2" in line
    assert "Hybrid search" in line
    assert "Ik wil AZ-900 halen" in line


def test_question_line_lists_the_techniques_that_are_on():
    line = format_question("q", 3, Config(bm25=True, rerank=True))
    assert "dense+bm25+rerank" in line


def test_question_line_says_custom_when_the_advanced_panel_drove_it():
    assert "custom" in format_question("q", None, Config())


def test_result_reports_the_retrievers_that_ran_and_what_they_returned():
    lines = format_result(_result(), Config(bm25=True), 1.5)
    text = "\n".join(lines)
    assert "dense 1" in text
    assert "bm25 2" in text
    assert "2 candidates" in text


def test_result_shows_the_rewritten_query_when_rewriting_ran():
    text = "\n".join(format_result(_result(rewritten="azure fundamentals certificaat"), Config(rewrite=True), 0.1))
    assert "azure fundamentals certificaat" in text


def test_result_says_off_for_the_stages_that_did_not_run():
    text = "\n".join(format_result(_result(), Config(), 0.1))
    assert "rewrite   off" in text
    assert "rerank    off" in text


def test_result_lists_the_used_chunks_with_their_rank_at_every_stage():
    text = "\n".join(format_result(_result(), Config(bm25=True, rerank=True), 0.1))
    assert "Bram Willems" in text
    assert "p.2" in text
    assert "dense#3" in text
    assert "rerank#1" in text


def test_result_reports_citations_and_elapsed_time():
    citations = [Citation(marker=1, chunk_id="a", title="Bram Willems", location="p.2")]
    text = "\n".join(format_result(_result(citations=citations), Config(citations=True), 1.25))
    assert "1 citation" in text
    assert "1.2s" in text


def test_result_reports_an_empty_retrieval_without_crashing():
    text = "\n".join(format_result(_result(candidates=[], used=[]), Config(), 0.1))
    assert "0 candidates" in text


def test_console_logging_mutes_the_hub_banner():
    import os

    install_console_logging()
    assert os.environ["HF_HUB_VERBOSITY"] == "error"


def test_console_logging_puts_the_pipeline_loggers_on_stderr_once():
    install_console_logging()
    install_console_logging()
    logger = logging.getLogger("rag")
    assert len(logger.handlers) == 1
    assert logging.getLogger("rag.llm").isEnabledFor(logging.INFO)


def test_the_critic_line_counts_the_checks_that_passed():
    line = format_critique([Check(True, "Igor Romy"), Check(False, "Jos Van Loock"), Check(True, "Vier houders")])
    assert "2/3" in line
    assert "Jos Van Loock" in line


def test_a_critic_that_said_nothing_says_so():
    assert "no verdict" in format_critique([])


def test_step_minus_one_names_itself_and_claims_no_technique():
    from web.trace import format_question

    line = format_question("Hoeveel credits?", -1, None)
    assert "step -1 \u00b7 Context" in line
    assert "no retrieval" in line


def test_usage_reads_as_a_cost_line():
    from web.trace import format_usage

    line = format_usage(
        {"input_tokens": 262_000, "cache_read_tokens": 0, "cost_usd": 1.31}, 2151, 16.4
    )
    assert "2151 chunks" in line
    assert "262k tokens" in line
    assert "$1.31" in line
    assert "16.4s" in line


def test_a_cached_prompt_says_so():
    from web.trace import format_usage

    line = format_usage(
        {"input_tokens": 262_000, "cache_read_tokens": 262_000, "cost_usd": 0.13}, 2151, 3.0
    )
    assert "cache read" in line


def test_usage_the_cli_did_not_report_is_not_a_crash():
    from web.trace import format_usage

    assert "2151 chunks" in format_usage({}, 2151, 16.4)
