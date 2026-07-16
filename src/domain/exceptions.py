class StandNotFoundError(Exception):
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.msg = f"Стенд не найден: {identifier}"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
