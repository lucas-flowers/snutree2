
'''
Convert a FamilyTree to DOT code.
'''

import dataclasses
from dataclasses import dataclass
from random import Random

from ...utilities.semester import Semester
from .config import Config, GRAPHS
from .create import Digraph, Subgraph, Attribute, Node, Edge
from .model import Component, ComponentType

# Functions to convert different types of objects to valid identifiers
IDENTIFIERS = {
    Semester: lambda semester: f'{semester.season}{semester.year}'.lower(),
    int: str,
}

# Fields that are templates, also requiring special handling
TEMPLATE_ATTRIBUTES = [
    'label',
]

def write(tree, stream, config: dict):
    raise NotImplementedError # TODO

def write_str(tree, config: dict):
    config = Config.from_dict(config)
    return Writer(config).write(tree)

def identify(value):
    return IDENTIFIERS[type(value)](value)

@dataclass
class Writer:
    '''
    The configuration treats graphs and classes identical to each other. But
    underneath, subgraphs are treated differently.

    Suppose nodes "id1" and "id2" are in the same graph and are also part of
    the same class with color blue. If we treated subgraphs just like we
    treated graphs, we would have something like this:

        graph "root" {
            "id1" [color="blue", label="Label 1", fillcolor="red"];
            "id2" [color="blue", label="Label 2", fillcolor="yellow"];
        }

    But in fact we can use DOT's attribute statements to write this with less
    redundancy:

        graph "root" {
            node [color="blue"];
            "id1" [label="Label 1", fillcolor="red"];
            "id2" [label="Label 2", fillcolor="yellow"];
        }

    Fields that won't be moved to the attribute statements are templated ones
    (namely, the 'label' field), since they'd be different for each node/edge.
    '''

    config: Config

    # TODO Custom cohorts

    def component_level_attributes(self, component_type, classes, data):
        '''
        Combine the classes and data into node/edge/graph attributes.
        '''

        class_to_attributes = getattr(self.config.classes, component_type.value)

        return {

            key: value.format(**data) if key in TEMPLATE_ATTRIBUTES else value

            # Use the class order in the config file, not the class list
            for cls in class_to_attributes.keys()
            if cls in classes
            for key, value in class_to_attributes[cls].items()

            # Do not include attributes inherited from graph-based classes
            # (unless they're templated attributes, like labels), since they
            # will be part of graph attributes instead
            if cls not in GRAPHS or key in TEMPLATE_ATTRIBUTES

        }

    def graph_level_attributes(self, component_type, classes):
        '''
        Combine the classes into a node/edge/graph attribute statement.
        '''

        class_to_attributes = getattr(self.config.classes, component_type.value)

        return {

            key: value

            # Use the class order in the config, not the class list
            for cls in class_to_attributes.keys()
            if cls in classes
            for key, value in class_to_attributes[cls].items()

            # Always include graph attributes, and any node or edge attributes
            # that aren't templated
            if component_type == ComponentType.GRAPH or key not in TEMPLATE_ATTRIBUTES

        }

    def attribute_statements(self, classes):
        '''
        Return a list of attribute statements based on the classes.
        '''
        component_type_to_attributes = {
            component_type: self.graph_level_attributes(component_type, classes)
            for component_type in ComponentType.__members__.values()
        }
        return [
            Component(
                type=component_type,
                identifiers=(),
                attributes=attributes,
            )
            for component_type, attributes in component_type_to_attributes.items()
            if attributes
        ]

    def rank_labels(self, graph_id, suffix, cohorts):
        '''
        Rank labels for the left or right side of the tree.
        '''
        return Subgraph(
            graph_id,
            *self.attribute_statements(['rank']),
            *(Node(
                f'{identify(cohort.rank)}{suffix}',
                **self.component_level_attributes(
                    ComponentType.NODE,
                    classes=cohort.classes,
                    data=cohort.data
                )
            ) for cohort in cohorts),
            *(Edge(
                f'{identify(cohort0.rank)}{suffix}',
                f'{identify(cohort1.rank)}{suffix}',
                **self.component_level_attributes(
                    ComponentType.EDGE,
                    classes=list({
                        # Use a dict to preserve both order and uniqueness
                        cls: None for cls in cohort0.classes + cohort1.classes
                    }),
                    data={
                        # TODO Is there a better way than prioritizing cohort1?
                        **cohort0.data,
                        **cohort1.data,
                    },
                )
            ) for cohort0, cohort1 in zip(cohorts[:-1], cohorts[1:])),
        )

    def write(self, tree):
        return str(self.root(tree))

    def root(self, tree):
        return Digraph(
            self.config.names.root_graph_name,
            *self.attribute_statements(['root']),
            self.rank_labels(
                graph_id=self.config.names.ranks_left_graph_name,
                suffix=self.config.names.rank_key_suffix_left,
                cohorts=tree.cohorts,
            ) if tree.cohorts is not None else None,
            self.tree(tree),
            self.rank_labels(
                graph_id=self.config.names.ranks_right_graph_name,
                suffix=self.config.names.rank_key_suffix_right,
                cohorts=tree.cohorts,
            ) if tree.cohorts is not None else None,
            *(map(self.ranks, tree.cohorts) if tree.cohorts is not None else ()),
        )

    def tree(self, tree):
        '''
        The actual entities and relationships in the tree.
        '''
        return Subgraph(
            self.config.names.tree_graph_name,
            *self.attribute_statements(['tree']),
            *self.nodes(tree),
            *self.config.nodes,
            *self.edges(tree),
            *self.config.edges,
        )

    def nodes(self, tree):
        if self.config.seed is not None:
            rng = Random(self.config.seed)
            shuffle = lambda families: rng.sample(families, k=len(families))
        else:
            shuffle = lambda families: families
        return [
            self.entity(entity)
            for family in shuffle(sorted(tree.families, key=min))
            for entity in sorted(family)
        ]

    def edges(self, tree):
        return map(self.relationship, sorted(tree.relationships))

    def entity(self, entity):
        return Node(
            entity.id,
            **self.component_level_attributes(
                ComponentType.NODE,
                classes=entity.classes,
                data=entity.data,
            ),
        )

    def relationship(self, relationship):
        return Edge(
            relationship.from_id,
            relationship.to_id,
            **self.component_level_attributes(
                ComponentType.EDGE,
                classes=relationship.classes,
                data=relationship.data,
            ),
        )

    def ranks(self, cohort):
        '''
        Group nodes of the same rank together.
        '''
        return Subgraph(
            Attribute(rank='same'),
            Node(f'{identify(cohort.rank)}L'),
            Node(f'{identify(cohort.rank)}R'),
            *map(Node, cohort.ids),
        )

