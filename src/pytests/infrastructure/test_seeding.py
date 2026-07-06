from src.domain.stand import Stand
from src.infrastructure.seeding import ensure_seeded
from src.pytests.commands.fakes import FakeStandRepository


def test_ensure_seeded_adds_missing_stands_as_free() -> None:
    repository = FakeStandRepository([])

    ensure_seeded(repository, ["akb1", "slplay4"])

    names = {stand.name for stand in repository.list_all()}
    assert names == {"akb1", "slplay4"}
    assert all(stand.status == "free" for stand in repository.list_all())


def test_ensure_seeded_does_not_touch_existing_stand() -> None:
    repository = FakeStandRepository(
        [Stand(name="akb1", status="occupied", occupied_by="alice")]
    )

    ensure_seeded(repository, ["akb1"])

    saved = repository.get_by_name("akb1")
    assert saved is not None
    assert saved.status == "occupied"
    assert saved.occupied_by == "alice"


def test_ensure_seeded_does_not_delete_stands_missing_from_list() -> None:
    repository = FakeStandRepository([Stand(name="legacy", status="free")])

    ensure_seeded(repository, ["akb1"])

    names = {stand.name for stand in repository.list_all()}
    assert "legacy" in names
    assert "akb1" in names
