from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


def test_day3_tables_registered() -> None:
    expected = {
        "users",
        "candidates",
        "jobs",
        "resumes",
        "skills",
        "candidate_skills",
        "job_skills",
        "candidate_embeddings",
        "job_embeddings",
        "candidate_scores",
        "audit_logs",
    }
    # async_jobs table introduced in Sprint 5 Phase 2
    expected.add("async_jobs")
    # ai_summaries table introduced in Sprint 6
    expected.add("ai_summaries")

    assert set(Base.metadata.tables) == expected


def test_skill_unique_index() -> None:
    skills = Base.metadata.tables["skills"]
    index = next(
        idx for idx in skills.indexes if idx.name == "idx_skills_skill_name"
    )

    assert index.unique is True
    assert list(index.columns.keys()) == ["skill_name"]


def test_candidate_score_xai_fields_and_constraints() -> None:
    scores = Base.metadata.tables["candidate_scores"]

    assert isinstance(scores.c.matched_skills.type, JSONB)
    assert isinstance(scores.c.missing_skills.type, JSONB)
    assert scores.c.recommendation.type.__class__.__name__ == "Text"

    assert any(
        isinstance(constraint, sa.UniqueConstraint)
        and constraint.name == "uq_candidate_scores_candidate_job"
        for constraint in scores.constraints
    )

    assert any(
        isinstance(constraint, sa.CheckConstraint)
        and constraint.name == "ck_candidate_scores_rank_positive"
        for constraint in scores.constraints
    )

    assert any(
        isinstance(constraint, sa.CheckConstraint)
        and constraint.name == "ck_candidate_scores_final_score"
        for constraint in scores.constraints
    )

    index_names = {idx.name for idx in scores.indexes}
    assert "idx_candidate_scores_job_rank" in index_names


def test_candidate_embedding_vector_indexes() -> None:
    embeddings = Base.metadata.tables["candidate_embeddings"]

    assert embeddings.c.embedding.type.__class__.__name__ == "VECTOR"
    assert any(idx.name == "idx_candidate_embeddings_candidate_id" for idx in embeddings.indexes)
    assert any(idx.name == "idx_candidate_vector" for idx in embeddings.indexes)


def test_job_embedding_vector_indexes() -> None:
    embeddings = Base.metadata.tables["job_embeddings"]

    assert embeddings.c.embedding.type.__class__.__name__ == "VECTOR"
    assert any(idx.name == "idx_job_embeddings_job_id" for idx in embeddings.indexes)
    assert any(idx.name == "idx_job_vector" for idx in embeddings.indexes)
