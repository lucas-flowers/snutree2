from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager, nullcontext
from dataclasses import dataclass
from types import SimpleNamespace
from typing import IO, ClassVar, ContextManager, Protocol, TypedDict

import MySQLdb
from sshtunnel import SSHTunnelForwarder


class SshConfig(TypedDict):
    ssh_address_or_host: tuple[str, int]
    ssh_username: str
    ssh_pkey: str
    remote_bind_address: tuple[str, int]
    allow_agent: bool


class SshTunnelContext(Protocol):
    local_bind_port: int


class SqlConfig(TypedDict):
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass
class SqlReaderConfig:
    sql: SqlConfig
    ssh: SshConfig | None = None


@dataclass
class SqlReader:
    extensions: ClassVar[list[str]] = [".sql"]

    config: SqlReaderConfig

    @contextmanager
    def forwarded(self) -> Iterator[SqlConfig]:
        context: ContextManager[SshTunnelContext]
        if self.config.ssh is None:
            context = nullcontext(SimpleNamespace(local_bind_port=self.config.sql["port"]))
        else:
            context = SSHTunnelForwarder(**self.config.ssh)

        with context as tunnel:
            yield SqlConfig(
                host=self.config.sql["host"],
                port=tunnel.local_bind_port,
                database=self.config.sql["database"],
                user=self.config.sql["user"],
                password=self.config.sql["password"],
            )

    def read(self, stream: IO[str]) -> Iterable[dict[str, str]]:
        query = stream.read()

        with self.forwarded() as config_sql:
            with closing(MySQLdb.Connect(**config_sql, use_unicode=True)) as connection:
                with connection.cursor(MySQLdb.cursors.DictCursor) as cursor:  # type: ignore[misc]
                    cursor.execute("SET NAMES 'utf8'")  # type: ignore[misc]
                    cursor.execute(query)  # type: ignore[misc]
                    return list(cursor.fetchall())  # type: ignore[misc]
