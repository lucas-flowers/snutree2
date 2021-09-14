from contextlib import closing, contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import (
    ClassVar,
    ContextManager,
    Iterable,
    Iterator,
    Optional,
    Protocol,
    TypedDict,
)

import MySQLdb
from sshtunnel import SSHTunnelForwarder

# MySQLdb and sshtunnel aren't well-typed:
# mypy: allow-any-expr,allow-any-explicit,allow-untyped-calls


class SshConfig(TypedDict):
    ssh_address_or_host: tuple[str, int]
    ssh_username: str
    ssh_pkey: str
    remote_bind_address: tuple[str, int]


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
    ssh: Optional[SshConfig] = None


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

    def read(self, path: Path) -> Iterable[dict[str, str]]:

        query = path.read_text()

        with self.forwarded() as config_sql:
            with closing(MySQLdb.Connect(**config_sql, use_unicode=True)) as connection:
                with connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
                    cursor.execute("SET NAMES 'utf8'")
                    cursor.execute(query)
                    return list(cursor.fetchall())
