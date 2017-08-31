#!/usr/bin/env python3
import csv
import sys
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Counter, deque
from random import Random
from pathlib import Path
from itertools import product
from faker import Faker

EXAMPLES_PATH = Path(__file__).parent

def semester_range(start, stop):
    for year, season in product(range(start, stop), ['Spring', 'Fall']):
        yield '{season} {year}'.format(season=season, year=year)

def write_example(example_generator, path):
    with path.open('w+') as stream:
        writer = csv.DictWriter(stream, example_generator.fieldnames)
        writer.writeheader()
        for row in example_generator():
            writer.writerow(row)

class RowGenerator(metaclass=ABCMeta):

    def __init__(self,
                 rank_range, # iterable of ranks
                 rank_size_min=0, # minimum size of a rank class
                 rank_size_max=10, # maximum size of a rank class
                 generations=None, # number of ranks a parent-child relationship can span
                 seed=0, # rng and faker seed
                 orphan_probability=0, # probability that a member will be an orphan given that there are eligible parents
                 ):

        self.ranks = rank_range
        self.rank_size_min = rank_size_min
        self.rank_size_max = rank_size_max
        self.generations = generations
        self.orphan_probability = orphan_probability
        self.faker = Faker()
        self.faker.seed(seed)
        self.rng = Random(seed)

    def __call__(self):

        recent_classes = deque([], maxlen=self.generations)
        for rank in self.ranks:
            rank_size = self.rng.randint(self.rank_size_min, self.rank_size_max)
            eligible_parents = set().union(*recent_classes)
            current_class = set()
            for _ in range(rank_size):
                parent_key = self.generate_parent_key(eligible_parents)
                key, row = self.generate_row(parent_key, rank)
                current_class.add(key)
                yield row
            recent_classes.append(current_class)

    def generate_parent_key(self, eligible_parents):
        if not eligible_parents:
            return None
        is_orphan = 1 - self.rng.random() < self.orphan_probability
        return eligible_parents.pop() if not is_orphan else None

    def generate_name(self):
        return '{first} {last}'.format(
            first=self.faker.first_name(),
            last=self.faker.last_name()
        )

    @abstractmethod
    def generate_row(self, parent_key, eligibles):
        raise NotImplementedError

    @abstractproperty
    def fieldnames(self):
        raise NotImplementedError

class BasicRowGenerator(RowGenerator):

    fieldnames = ['name', 'big_name', 'semester']

    def __init__(self, *args, **kwargs):
        self.used_names = Counter()
        super().__init__(*args, **kwargs)

    def generate_row(self, big_name, semester):
        key = name = self.generate_name()
        return key, dict(name=name, semester=semester,
                         **{'big_name' : big_name} if big_name else {})

    def generate_name(self):
        name = super().generate_name()
        self.used_names[name] += 1
        count = self.used_names[name]
        return name if count == 1 else '{name} (#{N})'.format(name=name, N=count)

class KeyedRowGenerator(RowGenerator):

    fieldnames = ['key', 'name', 'big_key', 'semester']

    def __init__(self, *args, **kwargs):
        self.current_key = 0
        super().__init__(*args, **kwargs)

    def use_next_key(self):
        self.current_key += 1
        return self.current_key

    def generate_row(self, big_key, semester):
        key = self.use_next_key()
        name = self.generate_name()
        return key, dict(key=key, name=name, semester=semester,
                         **{'big_key' : big_key} if big_key else {})

class CustomRowGenerator(KeyedRowGenerator):

    fieldnames = ['key', 'name', 'big_key', 'year']

    def generate_row(self, big_key, year):
        key = self.use_next_key()
        name = self.generate_name()
        return key, dict(key=key, name=name, year=year,
                         **{'big_key' : big_key} if big_key else {})


def main(names):

    generators = {
        'basic' : BasicRowGenerator(
            rank_range=semester_range(2010, 2020),
            generations=6,
            rank_size_min=8,
            rank_size_max=12,
            orphan_probability=0,
            seed=5
        ),
        'keyed' : KeyedRowGenerator(
            rank_range=semester_range(2000, 2020),
            generations=6,
            rank_size_min=0,
            rank_size_max=15,
            orphan_probability=.15,
            seed=1234
        ),
        'custom' : CustomRowGenerator(
            rank_range=range(1940, 2000),
            generations=6,
            rank_size_min=4,
            rank_size_max=8,
            orphan_probability=.15,
            seed=1234
        )
    }

    for name in names:

        generator = generators.get(name)
        if generator is None:
            fmt = 'Skipping {name!r}: Invalid example name {name!r}. Must be one of {names!r}.'
            print(fmt.format(name=name, names=set(generators.keys())), file=sys.stderr)
            continue

        path = EXAMPLES_PATH/name/(name+'.csv')
        if path.exists():
            fmt = 'Skipping {name!r}: File {path} exists.'
            print(fmt.format(name=name, path=path), file=sys.stderr)
            continue

        write_example(generator, path)

if __name__ == '__main__':
    main(sys.argv[1:])

