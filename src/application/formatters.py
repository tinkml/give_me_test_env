from src.domain.stand import Stand


class StandsMarkdownFormatter:
    HEADER = "| № | stand | status | user | since |"
    SEPARATOR = "|-|-|-|-|-|"

    @classmethod
    def format(cls, stands: list[Stand]) -> str:
        return cls._create_table(stands)

    @classmethod
    def _create_table(cls, stands: list[Stand]) -> str:
        rows = [cls._create_row(i, stand) for i, stand in enumerate(stands, start=1)]
        return "\n".join([cls.HEADER, cls.SEPARATOR, *rows])

    @classmethod
    def _create_row(cls, index: int, stand: Stand) -> str:
        row_builder_by_status = {
            "free": cls._free_stand,
            "occupied": cls._occupied_stand,
        }
        return row_builder_by_status[stand.status](index, stand)

    @staticmethod
    def _free_stand(index: int, stand: Stand) -> str:
        return f"| {index} | {stand.name} | ✅ Свободен | | |"

    @staticmethod
    def _occupied_stand(index: int, stand: Stand) -> str:
        since = stand.occupied_since.strftime("%Y-%m-%d %H:%M")
        return f"| {index} | {stand.name} | 🚫 Занят | {stand.occupied_by} | {since} |"
