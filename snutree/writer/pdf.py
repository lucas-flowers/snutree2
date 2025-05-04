import subprocess
from dataclasses import dataclass
from typing import Generic, TypeVar

from snutree.model.rank import AnyRank
from snutree.model.tree import FamilyTree
from snutree.writer.dot import DotWriter

MemberT = TypeVar("MemberT")


@dataclass
class PdfWriter(Generic[AnyRank, MemberT]):

    dot_writer: DotWriter[AnyRank, MemberT]

    def write(self, tree: FamilyTree[AnyRank, MemberT]) -> bytes:
        return subprocess.run(
            ["dot", "-T", "pdf", "-o", "-"],
            capture_output=True,
            check=True,
            input=self.dot_writer.write(tree),
        ).stdout
