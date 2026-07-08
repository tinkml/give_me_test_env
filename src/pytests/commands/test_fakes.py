from src.domain.stand import Stand
from src.pytests.commands.fakes import FakeStandRepository


async def test_list_all_returns_seeded_stands_in_order() -> None:
    stands = [Stand(name="akb1", status="free"), Stand(name="slplay4", status="free")]
    repository = FakeStandRepository(stands)

    assert [stand.name for stand in await repository.list_all()] == ["akb1", "slplay4"]


async def test_get_by_name_returns_none_when_missing() -> None:
    repository = FakeStandRepository([])

    assert await repository.get_by_name("akb1") is None


async def test_save_upserts_by_name() -> None:
    repository = FakeStandRepository([Stand(name="akb1", status="free")])

    await repository.save(Stand(name="akb1", status="occupied", occupied_by="alice"))

    saved = await repository.get_by_name("akb1")
    assert saved is not None
    assert saved.status == "occupied"
    assert saved.occupied_by == "alice"
