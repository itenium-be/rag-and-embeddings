from rag.models import WIZARD_STEPS, Config


def test_wizard_has_six_steps_and_accumulates():
    assert len(WIZARD_STEPS) == 6
    assert WIZARD_STEPS[0].config == Config()
    assert WIZARD_STEPS[1].config.bm25
    assert WIZARD_STEPS[2].config.bm25 and WIZARD_STEPS[2].config.rerank
    assert WIZARD_STEPS[3].config.rewrite
    assert WIZARD_STEPS[4].config.citations
    assert WIZARD_STEPS[5].config.aggregates


def test_aggregates_are_off_until_the_last_step():
    assert not Config().aggregates
    assert all(not s.config.aggregates for s in WIZARD_STEPS[:5])
