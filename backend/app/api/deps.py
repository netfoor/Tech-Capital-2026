"""Dependencias compartidas por los routers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import sesion

Sesion = Annotated[Session, Depends(sesion)]
