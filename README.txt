---
title: snutree
...

Introduction
============

Some Greek-letter organizations assign big brothers or big sisters ("bigs") to
new members ("littles"). This program visualizes such relationships as a family
tree, using Graphviz.

Usage
=====

Command Line
------------

### Basic Usage

The simplest usage of `snutree` is:

    snutree -o output.pdf input1.csv input2.csv ...

In this example, the CSV should have columns called `name`, `big_name`, and
`semester` where `semester`s are strings starting with "Fall" or "Spring" and
ending with a year (e.g., "Fall 2014" or "Spring 1956"). With this input,
`snutree` will append all the input tables together, convert them into a tree,
and output the tree using Graphviz. Each member will be put on a row
representing the semester they joined.

### Schemas

The (`name`, `big_name`, `semester`) headers consist of the "basic"
schema. There are a few other schemas available. They are:

| Schema  | Headers                                                                                        |
|---------+------------------------------------------------------------------------------------------------|
| basic   | name, big_name, semester                                                                |
| keyed   | id, name, big_id, semester                                                              |
| chapter | child, parent, founded                                                                         |
| sigmanu | badge, first_name, preferred_name, last_name, big_badge, status, semester, affiliations |

Changing schemas can be done with the `--schema` flag:

    snutree --schema chapter chapters.csv

In fact, a custom Python module may be used as a schema:

    snutree --schema /home/example/custom.py input.csv

Custom modules should validate the tables themselves and turn them into an
internal format `snutree` can read.

### SQL

The input format can be a SQL query:

    snutree --config config.yaml -o output.pdf query.sql

For a SQL query, one must have set up a YAML configuration file with
appropriate authentication options set. For example:

~~~yaml
readers:
  sql:
    host: '127.0.0.1'
    port: 3306
    user: 'root'
    passwd: 'secret'
    db: 'database_name'
    # Credentials for tunneling queries through SSH (recommended)
    ssh:
      host: 'example.com'
      port: 22
      user: 'example'
      public_key: '/home/example/.ssh/id_rsa'
~~~

Note that the query must rename the column headers to match the `snutree` schema.

<!-- TODO

GUI
---

Advanced Usage
==============

Installation
============

Prerequisites
-------------

Installing
----------

Extra Features
--------------

-->

Versioning
==========

This project uses [Semantic Versioning](http://semver.org/).

License
=======

This project is licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).

