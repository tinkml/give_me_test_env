import pytest
from sqlalchemy.orm import Session

from src.domain.stand import Stand
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base
from src.infrastructure.repository import SqlAlchemyStandRepository


@pytest.fixture
def session() -> Session:
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)
    with session_factory() as db_session:
        yield db_session


def test_save_and_get_by_name_round_trip(session: Session) -> None:
    repository = SqlAlchemyStandRepository(session)
    repository.save(Stand(name="akb1", status="free"))

    result = repository.get_by_name("akb1")

    assert result is not None
    assert result.name == "akb1"
    assert result.status == "free"


def test_get_by_name_returns_none_when_missing(session: Session) -> None:
    repository = SqlAlchemyStandRepository(session)

    assert repository.get_by_name("missing") is None


def test_save_updates_existing_row_by_name(session: Session) -> None:
    repository = SqlAlchemyStandRepository(session)
    repository.save(Stand(name="akb1", status="free"))

    repository.save(Stand(name="akb1", status="occupied", occupied_by="alice"))

    result = repository.get_by_name("akb1")
    assert result is not None
    assert result.status == "occupied"
    assert result.occupied_by == "alice"


def test_list_all_preserves_insertion_order(session: Session) -> None:
    repository = SqlAlchemyStandRepository(session)
    repository.save(Stand(name="akb1", status="free"))
    repository.save(Stand(name="slplay4", status="free"))

    result = repository.list_all()

    assert [stand.name for stand in result] == ["akb1", "slplay4"]
