"""Basic backend tests."""

import pytest
from rudra.research.engine import CredibilityEvaluator, SourceType


class TestCredibilityEvaluator:
    def test_trusted_domain(self):
        score = CredibilityEvaluator.score("https://www.reuters.com/article", SourceType.NEWS)
        assert score >= 0.9

    def test_unknown_domain(self):
        score = CredibilityEvaluator.score("https://random-blog.com/post", SourceType.WEB)
        assert score == 0.5

    def test_academic_base_score(self):
        score = CredibilityEvaluator.score("https://unknown.edu/paper", SourceType.ACADEMIC)
        assert score >= 0.85

    def test_user_memory_highest(self):
        score = CredibilityEvaluator.score("memory://abc", SourceType.USER_MEMORY)
        assert score >= 0.9
