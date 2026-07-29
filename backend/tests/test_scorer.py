from app.services.director.scorer import PromptScorer


def test_prompt_scorer_weak_prompt():
    score, label, feedback = PromptScorer.evaluate("bottle")
    assert 0 <= score <= 50
    assert label in ("Basic", "Moderate")
    assert len(feedback) > 0


def test_prompt_scorer_detailed_prompt():
    detailed_prompt = (
        "A luxury perfume bottle rotating on black marble with warm golden volumetric lighting. "
        "Macro 35mm anamorphic tracking camera shot."
    )
    score, label, feedback = PromptScorer.evaluate(detailed_prompt)
    assert score >= 80
    assert label in ("Detailed", "Director Level")
    assert len(feedback) == 0


def test_prompt_scorer_bounds():
    empty_score, _, _ = PromptScorer.evaluate("   ")
    assert empty_score == 0

    overlong_prompt = "luxury perfume bottle rotating on black marble lighting shot " * 10
    score, _, _ = PromptScorer.evaluate(overlong_prompt)
    assert 0 <= score <= 100
