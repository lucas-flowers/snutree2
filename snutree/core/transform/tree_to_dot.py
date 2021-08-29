from dataclasses import dataclass
from typing import List, Optional, TypeVar

from snutree.core.model.tree import Cohort, Tree
from snutree.tool.dot.declarative import Digraph
from snutree.tool.dot.model import _Statement

T = TypeVar("T")


@dataclass
class NameConfig:
    root_graph: str
    ranks_graph_left: str
    ranks_graph_left_suffix: str
    ranks_graph_right: str
    ranks_graph_right_suffix: str


@dataclass
class Config:
    names: NameConfig


def create_root(tree: Tree[T], config: Config) -> _Statement:
    return Digraph(
        config.names.root_graph,
        *create_attributes(),
        create_ranks(
            graph_id=config.names.ranks_graph_left,
            cohorts=tree.cohorts,
            suffix=config.names.ranks_graph_right_suffix,
        ),
        create_tree(tree),
        create_ranks(
            graph_id=config.names.ranks_graph_right,
            cohorts=tree.cohorts,
            suffix=config.names.ranks_graph_right_suffix,
        ),
        *map(create_cohort, tree.cohorts or []),
    )


# pylint: disable=unused-argument


def create_attributes(obj: None = None) -> List[_Statement]:
    ...


def create_ranks(graph_id: str, cohorts: Optional[List[Cohort]], suffix: str) -> Optional[_Statement]:
    ...


def create_tree(tree: Tree[T]) -> _Statement:
    ...


def create_cohort(cohort: Cohort) -> _Statement:
    ...
