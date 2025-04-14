from sqlalchemy.orm import (
    registry,
)
print("--------called--------")
REG = registry()
"""
共用一个REG创建表
"""
