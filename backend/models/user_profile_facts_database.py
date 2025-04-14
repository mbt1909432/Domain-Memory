from database.reg_instance import REG
from sqlalchemy import VARCHAR, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


@REG.mapped_as_dataclass
class UserProfileFacts(Base):
    __tablename__ = "user_profile_facts"
    domain: Mapped[str] = mapped_column(VARCHAR(50))
    attribute: Mapped[str] = mapped_column(VARCHAR(100))
    description: Mapped[str] = mapped_column(VARCHAR(500))

