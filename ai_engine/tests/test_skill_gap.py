from __future__ import annotations

from ai_engine.matching.skill_gap_service import SkillGapService


def test_perfect_match():
    service = SkillGapService()
    candidate = ["Python", "Docker", "FastAPI"]
    required = ["Python", "FastAPI", "Docker"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 100.0
    assert result.matching_skills == ["Python", "FastAPI", "Docker"]
    assert result.missing_skills == []


def test_partial_match():
    service = SkillGapService()
    candidate = ["Python", "Django"]
    required = ["Python", "FastAPI", "Docker"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == round((1/3) * 100, 2)
    assert result.matching_skills == ["Python"]
    assert result.missing_skills == ["FastAPI", "Docker"]


def test_no_match():
    service = SkillGapService()
    candidate = ["Java", "Spring"]
    required = ["Python", "FastAPI"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 0.0
    assert result.matching_skills == []
    assert result.missing_skills == ["Python", "FastAPI"]


def test_empty_candidate_skills():
    service = SkillGapService()
    candidate = []
    required = ["Python", "FastAPI"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 0.0
    assert result.matching_skills == []
    assert result.missing_skills == ["Python", "FastAPI"]


def test_empty_required_skills():
    service = SkillGapService()
    candidate = ["Python", "FastAPI"]
    required = []
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 100.0
    assert result.matching_skills == []
    assert result.missing_skills == []


def test_duplicate_skills():
    service = SkillGapService()
    candidate = ["Python", "python", "Docker"]
    required = ["Python", "PYTHON", "FastAPI", "Fastapi"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 50.0
    assert len(result.matching_skills) == 1
    assert result.matching_skills[0].lower() == "python"
    assert len(result.missing_skills) == 1
    assert result.missing_skills[0].lower() == "fastapi"


def test_mixed_casing():
    service = SkillGapService()
    candidate = ["pYtHoN", "FASTAPI"]
    required = ["Python", "FastAPI"]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 100.0
    assert result.matching_skills == ["Python", "FastAPI"]
    assert result.missing_skills == []


def test_skill_normalization():
    service = SkillGapService()
    candidate = ["  Python  ", "FastAPI\n"]
    required = ["\tPython", " FastAPI "]
    
    result = service.analyze(candidate, required)
    
    assert result.match_percentage == 100.0
    assert result.matching_skills == ["Python", "FastAPI"]
    assert result.missing_skills == []
