import json
import logging
from contextlib import contextmanager
from typing import Any, Optional

from open_webui.internal.wrappers import register_connection
from open_webui.env import (
    OPEN_WEBUI_DIR,
    DATABASE_URL,
    DATABASE_SCHEMA,
    SRC_LOG_LEVELS,
    DATABASE_POOL_MAX_OVERFLOW,
    DATABASE_POOL_RECYCLE,
    DATABASE_POOL_SIZE,
    DATABASE_POOL_TIMEOUT,
)
from peewee_migrate import Router
from sqlalchemy import Dialect, create_engine, MetaData, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from typing_extensions import Self

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("DB", logging.INFO))


class JSONField(types.TypeDecorator):
    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Any], dialect: Dialect) -> Any:
        return json.dumps(value)

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Any:
        if value is not None:
            return json.loads(value)

    def copy(self, **kw: Any) -> Self:
        return JSONField(self.impl.length)

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


def prepare_database_url(url: str) -> str:
    if "supabase" in url and "sslmode=" not in url:
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"
    return url.replace("postgresql://", "postgres://")


def handle_peewee_migration(database_url: str):
    db = None
    try:
        fixed_url = prepare_database_url(database_url)
        db = register_connection(fixed_url)
        migrate_dir = OPEN_WEBUI_DIR / "internal" / "migrations"
        router = Router(db, logger=log)

        db.connect(reuse_if_open=True)
        if not db.is_closed():
            log.info("✅ Database connected successfully, applying migrations...")
            router.run()
        else:
            log.warning("⚠️ Database connection was closed immediately after opening.")
    except Exception as e:
        log.error(f"❌ Failed to initialize or migrate database: {e}")
        log.error("🚨 Continuing without database connection. Some features may be unavailable.")
    finally:
        if db and not db.is_closed():
            db.close()


try:
    handle_peewee_migration(DATABASE_URL)
except Exception as e:
    log.error(f"🔥 Fatal error during database initialization: {e}")


SQLALCHEMY_DATABASE_URL = prepare_database_url(DATABASE_URL)

if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    if DATABASE_POOL_SIZE > 0:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_POOL_MAX_OVERFLOW,
            pool_timeout=DATABASE_POOL_TIMEOUT,
            pool_recycle=DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,
            poolclass=QueuePool,
        )
    else:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            poolclass=NullPool,
        )

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)
metadata_obj = MetaData(schema=DATABASE_SCHEMA)
Base = declarative_base(metadata=metadata_obj)
Session = scoped_session(SessionLocal)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = contextmanager(get_session)
