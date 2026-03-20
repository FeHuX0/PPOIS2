from collections.abc import Iterator
from contextlib import contextmanager
from typing import Callable, ContextManager

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

SessionFactory = Callable[[], Session]
SessionScopeFactory = Callable[[], ContextManager[Session]]


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


@contextmanager
def session_scope(session_factory: SessionFactory) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_session_scope_factory(session_factory: SessionFactory) -> SessionScopeFactory:
    def _session_scope_factory() -> ContextManager[Session]:
        return session_scope(session_factory)

    return _session_scope_factory
