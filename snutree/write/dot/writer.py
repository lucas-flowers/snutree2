
'''
Convert a FamilyTree to DOT code.
'''

from random import Random

from ...utilities import get
from .config import validate, GRAPHS, TEMPLATE_ATTRIBUTES
from .create import Graph, Digraph, Subgraph, Attribute, Node, Edge

def write(tree, stream, config=None):
    raise NotImplementedError # TODO

def write_str(tree, config=None):
    return Writer(config or {}).write(tree)

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

    def __init__(self, config):
        validate(config)
        self.config = config

    @property
    def custom_nodes(self):
        return [
            Node(identifier, **attributes)
            for identifier, attributes
            in get(self.config, 'custom', 'node').items()
        ]

    @property
    def custom_edges(self):
        return [
            Edge(*identifiers.split(','), **attributes)
            for identifiers, attributes
            in get(self.config, 'custom', 'edge').items()
        ]

    # TODO Custom cohorts

    def attribute_list(self, component_type, classes, data):
        '''
        Combine the classes and data into node/edge/graph attributes.
        '''
        return {

            key: value.format(**data) if key in TEMPLATE_ATTRIBUTES else value

            # Use the class order in the config file, not the class list
            for cls in get(self.config, 'class', component_type).keys()
            if cls in classes
            for key, value in self.config['class'][component_type][cls].items()

            # Do not include attributes inherited from graph-based classes
            # (unless they're templated attributes, like labels), since they
            # will be part of graph attributes instead
            if cls not in GRAPHS or key in TEMPLATE_ATTRIBUTES

        }

    def attribute_statements(self, graph_id):
        '''
        Return a list of attribute statements for the given (sub)graph.
        '''

        graph_attributes, node_attributes, edge_attributes = ({

            key: value
            for key, value in get(self.config, 'class', component, graph_id).items()

            # Always include graph attributes, and any node or edge attributes
            # that aren't templated
            if component == 'graph' or key not in TEMPLATE_ATTRIBUTES

        } for component in ('graph', 'node', 'edge'))

        attribute_statements = [
            graph_attributes and Graph(**graph_attributes),
            node_attributes and Node(**node_attributes),
            edge_attributes and Edge(**edge_attributes),
        ]

        return [
            attribute_statement
            for attribute_statement in attribute_statements
            if attribute_statement
        ]

    def rank_labels(self, suffix, cohorts):
        '''
        Rank labels for the left or right side of the tree.
        '''
        # TODO Remove suffix; just use graph_id or something
        return Subgraph(
            f'rank{suffix}',
            *self.attribute_statements('rank'),
            *(Node(
                f'{cohort.id}{suffix}',
                **self.attribute_list(
                    'node',
                    classes=['root', 'rank'],
                    data={'rank': cohort.rank},
                )
            ) for cohort in cohorts),
            *(Edge(
                f'{cohort0.id}{suffix}',
                f'{cohort1.id}{suffix}',
                **self.attribute_list(
                    'edge',
                    classes=['root', 'rank'],
                    data={},
                )
            ) for cohort0, cohort1 in zip(cohorts[:-1], cohorts[1:])),
        )

    def write(self, tree):
        return str(self.root(tree))

    def root(self, tree):
        return Digraph(
            'root',
            *self.attribute_statements('root'),
            self.rank_labels('Left'[0], tree.cohorts) if tree.cohorts is not None else None,
            self.tree(tree),
            self.rank_labels('Right'[0], tree.cohorts) if tree.cohorts is not None else None,
            *(map(self.ranks, tree.cohorts) if tree.cohorts is not None else ()),
        )

    def tree(self, tree):
        '''
        The actual entities and relationships in the tree.
        '''
        return Subgraph(
            'tree',
            *self.attribute_statements('tree'),
            *self.nodes(tree),
            *self.custom_nodes,
            *self.edges(tree),
            *self.custom_edges,
        )

    def nodes(self, tree):
        if self.config.get('seed'):
            rng = Random(self.config['seed'])
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
            **self.attribute_list(
                'node',
                classes=entity.classes,
                data=entity.data,
            ),
        )

    def relationship(self, relationship):
        return Edge(
            relationship.from_id,
            relationship.to_id,
            **self.attribute_list(
                'edge',
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
            Node(f'{cohort.rank}L'),
            Node(f'{cohort.rank}R'),
            *map(Node, cohort.ids),
        )

