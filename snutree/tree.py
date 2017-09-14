import random
from enum import Enum
from collections import Iterable
from abc import ABCMeta, abstractmethod
from networkx import DiGraph
from networkx.algorithms.components import weakly_connected_components
from .errors import SnutreeError
from .utilities.logging import logged

###############################################################################
###############################################################################
#### Entities on the Tree                                                  ####
###############################################################################
###############################################################################

class TreeEntity(metaclass=ABCMeta):
    '''
    Represents an entity on the Family Tree. TreeEntities should have these
    fields:

        + key: The key to be used in DOT

        + _rank: A private field storing a rank ID, which is assumed to be
        some kind of integer-compatible object (e.g., actual integers
        representing years, a Semester object, or other ordered types that
        integers can be added to). This field might be allowed to remain
        unset (for example, when the tree is drawn without using ranks), though
        it will raise an error if used before it is set.
    '''

    def __init__(self, key, rank=None):
        self.key = key
        self._rank = rank

    def is_ranked(self):
        return bool(self._rank)

    @property
    def rank(self):
        if self._rank:
            return self._rank
        else:
            code = TreeErrorCode.ACCESS_MISSING_RANK
            msg = 'missing rank value for entity {key!r}'.format(key=self.key)
            raise TreeError(code, msg)

    @rank.setter
    def rank(self, value):
        self._rank = value

class Member(TreeEntity, metaclass=ABCMeta):
    '''
    Represents a member of the organization. Subclasses should implement the
    label property, which produces a labels for drawing. Subclasses should also
    set the `parent` field to the key of each Member's parent.
    '''

    @property
    @abstractmethod
    def label(self):
        pass

###############################################################################
###############################################################################
#### Family Tree                                                           ####
###############################################################################
###############################################################################

class FamilyTree:
    '''
    Representation of the family tree. Each key is a string and each node is a
    dictionary containing 'entity', which stores a TreeEntity for the
    corresponding key. TreeEntities may also be Members.

    The edges between Members are the big-little relationships. These are
    created from the parent fields when Members are loaded into the tree.
    Non-Members may have edges, but these do not represent big-little
    relationships.
    '''

    @logged
    def __init__(self, members, seed=0):
        self.graph = DiGraph()
        self.seed = seed
        self.add_members(members)

    ###########################################################################
    #### Members                                                           ####
    ###########################################################################

    def add_members(self, members):
        '''
        Add the members to the tree, along with their relationships and families.
        '''
        self.add_entities(members)
        self.add_member_relationships()
        self.mark_families()

    def add_member_relationships(self):
        '''
        Connect all Members in the tree, based on the value of their parent
        field, by adding the edge (parent, member). Parents must also be
        Members (to add non-Members as parent nodes, use custom edges).
        '''
        for member in self.members():
            if member.parent:
                self.add_member_relationship(member)

    def add_member_relationship(self, member):
        '''
        Add an edge for the member and its parent to the tree. Ensure that the
        parent actually exists in the tree already and that the parent is on
        the same rank or on a rank before the member.
        '''

        ckey = member.key
        pkey = member.parent

        if pkey not in self:
            code = TreeErrorCode.PARENT_UNKNOWN
            msg = 'member {ckey!r} has unknown parent: {pkey!r}'.format(ckey=ckey, pkey=pkey)
            raise TreeError(code, msg)

        parent = self[pkey]['entity']

        if member.rank and parent.rank and member.rank < parent.rank:
            code = TreeErrorCode.PARENT_NOT_PRIOR
            msg = 'rank {rank!r} of member {ckey!r} cannot be prior to rank of parent {pkey!r}: {parent_rank!r}'.format(rank=member.rank, ckey=ckey, pkey=pkey, parent_rank=parent.rank)
            raise TreeError(code, msg)

        self.add_edge(pkey, ckey)

    def mark_families(self):
        '''
        Mark all families in the tree by adding a 'family' attribute to each
        Member node, which is a dictionary shared by all members of that
        family.
        '''

        # Families are weakly connected components of the members-only graph
        members_only = self.member_subgraph()
        families = weakly_connected_components(members_only)

        # Add a pointer to each member's family subgraph
        for family in families:
            family_dict = {}
            for key in family:
                self[key]['family'] = family_dict

    ###########################################################################
    #### Entities                                                          ####
    ###########################################################################

    def add_entities(self, entities):
        '''
        Add the entities to the tree.
        '''
        for entity in entities:
            self.add_entity(entity)

    def add_entity(self, entity, **attributes):
        '''
        Add the entity with the given extra attributes to the tree. Catch any
        duplicates.
        '''
        key = entity.key
        if key in self:
            code = TreeErrorCode.DUPLICATE_ENTITY
            msg = 'duplicate entity key: {key!r}'.format(key=key)
            raise TreeError(code, msg)
        self.graph.add_node(key, entity=entity, **attributes)

    def get_rank_bounds(self):
        '''
        Find and return the values of the highest and lowest ranks in use.
        '''
        min_rank, max_rank = float('inf'), float('-inf')
        for entity in self._iter('entity', keys=False):
            rank = entity.rank
            if rank and min_rank > rank:
                min_rank = rank
            if rank and max_rank < rank:
                max_rank = rank
        return min_rank, max_rank

    ###########################################################################
    #### Iterators                                                         ####
    ###########################################################################

    def _iter(self, *attributes, keys=True, nodes=False):
        '''
        Iterates of the nodes of the graph, yielding tuples of the form:

            (<KEY>, <ATTRIBUTE0>, <ATTRIBUATE1>, ..., <NODE>)

        By default, returns only the keys. Setting keys=False will remove the
        keys, setting any kwargs to some attribute name will include those
        attributes (in the order they are written), and setting nodes=True will
        include the entire node attribute dictionary at the end.

        If only one element will be in the yielded tuples, that element will
        be yielded directly (i.e., not as a singleton tuple).
        '''
        for key, node in self.graph.nodes_iter(data=True):
            yielded = (
                    *((key,) if keys else ()),
                    *tuple([node[attr] for attr in attributes]),
                    *((node,) if nodes else ())
                    )
            yield yielded[0] if len(yielded) == 1 else yielded

    def keys(self):
        '''
        Yields all the keys in the tree.
        '''
        yield from self._iter()

    def nodes(self):
        '''
        Yields all the nodes in the tree.
        '''
        yield from self._iter(keys=False, nodes=True)

    def items(self):
        '''
        Yields all tree's keys and their nodes.
        '''
        yield from self._iter(nodes=True)

    def members(self):
        '''
        Yields all the Member objects in the tree's nodes.
        '''
        for entity in self._iter('entity', keys=False):
            if isinstance(entity, Member) :
                yield entity

    def orphans(self):
        '''
        Yields all Members in the tree that have no parent nodes.
        '''
        for key, in_degree in self.graph.in_degree().items():
            entity = self[key]['entity']
            if in_degree == 0 and isinstance(entity, Member):
                yield entity

    def singletons(self):
        '''
        Yields all Members that neither have parent nodes nor child nodes.
        '''
        for key, degree in self.graph.degree_iter():
            entity = self[key]['entity']
            if degree == 0 and isinstance(entity, Member):
                yield entity

    def edges(self):
        '''
        Yields all the edge dictionaries in the tree.
        '''
        for _, _, edge in self.graph.edges_iter(data=True):
            yield edge

    def member_subgraph(self):
        '''
        Returns a subgraph consisting only of members.
        '''
        member_keys = (member.key for member in self.members())
        return self.graph.subgraph(member_keys)

    ###########################################################################
    #### Ordered Iterators                                                 ####
    ###########################################################################

    def ordered_items(self):
        '''
        Yields this graph's nodes and keys in a guaranteed consistent order.

        First: The (weakly) connected components of the graph are put in a
        list. The components are then sorted by the minimum
        (lexicographically-speaking) key they contain. Then, the tree's RNG
        seed is used to shuffle the connected components. A few notes:

            + The components are randomized because strange behavior might
            occur if the nodes are left to be in the same order produced by
            normal iteration. That would make the resulting graph look ugly.

            + The user can set the tree's seed field to help obtain the same
            result every time the program is run on the same input. The user
            can also change the seed to change the layout instead of fiddling
            around with the drawn tree itself.

            + The components are sorted even though they are then immediately
            shuffled again. This is to ensure the rng.shuffle function produces
            the same result for the same seed.

        Second: The keys and node dictionaries for all of the nodes in all of
        the components are then returned in lexicographical order.
        '''
        components = weakly_connected_components(self.graph)
        components = sorted(components, key = lambda component : min(component, key=str))
        rng = random.Random(self.seed)
        rng.shuffle(components)
        for component in components:
            for key in sorted(component, key=str):
                yield key, self[key]

    def ordered_edges(self):
        '''
        Yields this graph's edges in a guaranteed consistent order. Each result
        returned is a tuple containing a parent key, a child key, and the edge
        dictionary of the edge between them. The edges are sorted first by
        parent key, then child key, then the string form of the edge's
        attribute dictionary.
        '''
        edges = self.graph.edges(data=True)
        def sort_key(arg):
            parent_key, child_key, edge_dict = arg
            return (parent_key, child_key, str(edge_dict))
        yield from sorted(edges, key=sort_key)

    ###########################################################################
    #### Miscellaneous                                                     ####
    ###########################################################################

    def add_edges(self, edges, **attributes):
        self.graph.add_edges_from(edges, **attributes)

    def add_edge(self, key, pkey, **attributes):
        self.graph.add_edge(key, pkey, **attributes)

    def remove(self, key_or_keys):
        if isinstance(key_or_keys, Iterable):
            self.graph.remove_nodes_from(key_or_keys)
        else:
            self.graph.remove_node(key_or_keys)

    def __contains__(self, key):
        return key in self.graph

    def __getitem__(self, key):
        return self.graph.node[key]

###############################################################################
###############################################################################
#### Errors                                                                ####
###############################################################################
###############################################################################

class TreeError(SnutreeError):
    '''
    Raised after any tree-related errors occur. The errno should be filled with
    one of the TreeErrorCodes, which makes testing errors easier.
    '''

    def __init__(self, errno, msg=None):
        self.errno = errno
        self.message = msg

    def __str__(self):
        return self.message

TreeErrorCode = Enum('TreeErrorCode', (
        'ACCESS_MISSING_RANK',
        'DUPLICATE_ENTITY',
        'PARENT_UNKNOWN',
        'PARENT_NOT_PRIOR',
        ))

