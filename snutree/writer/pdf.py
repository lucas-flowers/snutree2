import subprocess
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import Generic, TypeVar

from snutree.model.rank import AnyRank
from snutree.model.tree import FamilyTree
from snutree.writer.dot import DotWriter

MemberT = TypeVar("MemberT")


class PdfWriterError(Exception):
    pass


@dataclass
class PdfWriter(Generic[AnyRank, MemberT]):

    dot_writer: DotWriter[AnyRank, MemberT]

    def write(self, tree: FamilyTree[AnyRank, MemberT]) -> bytes:
        try:
            return subprocess.run(
                ["dot", "-T", "pdf"],
                capture_output=True,
                input=self.dot_writer.write(tree),
                check=True,
            ).stdout
        except CalledProcessError as e:
            stderr: str = e.stderr
            raise RuntimeError(f"failed to compile dot file to PDF: {stderr}") from e
