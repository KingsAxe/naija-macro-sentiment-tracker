from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session

DbSession = Annotated[Session, Depends(get_db_session)]
