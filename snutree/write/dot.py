
from ..model.dot import Graph, Digraph, Subgraph, Attribute, Node, Edge

def write(tree, config):
    write = Write(config)
    dot = write.family_tree('family_tree', tree)
    return str(dot)

class Write:

    def __init__(self, config):
        self.config = config

    def family_tree(self, graph_id, tree):
        return Digraph(
            graph_id,
            *self.graph_attributes(graph_id),
            self.rank_labels('datesL', 'L', tree.cohorts) if tree.cohorts is not None else None,
            self.tree('members', tree.entities, tree.relationships),
            self.rank_labels('datesR', 'R', tree.cohorts) if tree.cohorts is not None else None,
            *map(self.ranks, tree.cohorts),
        )

    def graph_attributes(self, graph_id):
        '''
        Attributes for subgraphs.
        '''
        return [
            Component(**self.config[component][graph_id])
            for Component, component in (
                (Graph, 'graph'),
                (Node, 'node'),
                (Edge, 'edge'),
            )
            if self.config.get(component, {}).get(graph_id)
        ]

    def rank_labels(self, graph_id, suffix, cohorts):
        '''
        Rank labels for the left or right side of the tree.
        '''
        # TODO Remove suffix; just use graph_id or something
        return Subgraph(
            graph_id,
            *self.graph_attributes(graph_id),
            *(Node(
                f'{cohort.id}{suffix}',
                **self.component_attributes('node', cohort.classes, cohort.data)
            ) for cohort in cohorts),
            *(Edge(
                f'{cohort0.id}{suffix}',
                f'{cohort1.id}{suffix}',
                **self.component_attributes('edge', set(), {}) # TODO classes/data
            ) for cohort0, cohort1 in zip(cohorts[:-1], cohorts[1:])),
        )

    def tree(self, graph_id, entities, relationships):
        '''
        The actual entities and relationships in the tree.
        '''
        return Subgraph(
            graph_id,
            *self.graph_attributes('members'),
            *map(self.entity, entities),
            *map(self.relationship, relationships),
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

    def component_attributes(self, component_type, classes, data):
        '''
        Attributes for nodes and edges.
        '''
        return {
            # Maintain the class order in the config file, instead of using the
            # order found in the class list
            key: value.format(**data) if key == 'label' else value
            for cls in self.config[component_type].keys()
            if cls in classes
            for key, value in self.config[component_type][cls].items()
        }

    def entity(self, entity):
        return Node(
            entity.id,
            **self.component_attributes('node', entity.classes, entity.data),
        )

    def relationship(self, relationship):
        return Edge(
            relationship.from_id,
            relationship.to_id,
            **self.component_attributes('edge', relationship.classes, relationship.data),
        )

