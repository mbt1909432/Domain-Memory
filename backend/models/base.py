import uuid
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


@dataclass
class Base:
    __abstract__ = True


    id: Mapped[str] = mapped_column(
        VARCHAR(36),
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),  # 生成字符串 UUID,
        init=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), init=False, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
        comment="更新时间",
    )