from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import RawText
from app.services.analysis import analyze_pending_sentiments


@dataclass
class FakeConfidenceScores:
    positive: float
    neutral: float
    negative: float


@dataclass
class FakeAssessment:
    text: str
    sentiment: str


@dataclass
class FakeTarget:
    text: str
    sentiment: str


@dataclass
class FakeMinedOpinion:
    target: FakeTarget
    assessments: list[FakeAssessment]


@dataclass
class FakeSentence:
    mined_opinions: list[FakeMinedOpinion]


@dataclass
class FakeResult:
    sentiment: str
    confidence_scores: FakeConfidenceScores
    sentences: list[FakeSentence]
    is_error: bool = False


class FakeSentimentClient:
    def analyze_sentiment(self, documents: list[dict[str, str]], *, show_opinion_mining: bool):
        assert show_opinion_mining is True
        assert len(documents) == 2
        return [
            FakeResult(
                sentiment="negative",
                confidence_scores=FakeConfidenceScores(positive=0.1, neutral=0.2, negative=0.7),
                sentences=[
                    FakeSentence(
                        mined_opinions=[
                            FakeMinedOpinion(
                                target=FakeTarget(text="fuel price", sentiment="negative"),
                                assessments=[FakeAssessment(text="high", sentiment="negative")],
                            )
                        ]
                    )
                ],
            ),
            FakeResult(
                sentiment="positive",
                confidence_scores=FakeConfidenceScores(positive=0.8, neutral=0.1, negative=0.1),
                sentences=[],
            ),
        ]


def test_analyze_pending_sentiments_persists_sentiment_and_targets(tmp_path: Path) -> None:
    database_path = tmp_path / "analysis.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.add_all(
            [
                RawText(source="x", topic_label="Fuel Price", content="Fuel prices are too high"),
                RawText(source="x", topic_label="FX Rate", content="The naira looks stable today"),
            ]
        )
        session.commit()

    with SessionLocal() as session:
        result = analyze_pending_sentiments(session=session, client=FakeSentimentClient())
        sentiment_count = session.execute(text("select count(*) from analyzed_sentiments")).scalar_one()
        target_count = session.execute(text("select count(*) from opinion_targets")).scalar_one()
        assessment_count = session.execute(text("select count(*) from opinion_assessments")).scalar_one()
        synthetic_targets = session.execute(
            text("select count(*) from opinion_targets where target_name like '%: %'")
        ).scalar_one()

    assert result.analyzed_count == 2
    assert result.target_count == 1
    assert result.assessment_count == 1
    assert result.skipped_count == 0
    assert sentiment_count == 2
    assert target_count == 1
    assert assessment_count == 1
    assert synthetic_targets == 0
