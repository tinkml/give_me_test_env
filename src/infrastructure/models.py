from datetime import datetime

from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class StandModel(Base):
    __tablename__ = "stands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[str]
    occupied_by: Mapped[str | None]
    occupied_since: Mapped[datetime | None]
