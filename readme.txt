---
title: snutree
...

Introduction
============

Some organizations, like Greek-letter organizations, assign "bigs" (i.e., big
brothers or big sisters) to new members. This script visualizes such
relationships using Graphviz. It was originally developed for use by the Delta
Alpha Chapter of Sigma Nu Fraternity.

Basic Example
=============

#. Create a CSV file with the following fields for each row:

    + `name`: A member's name

    + `big_name`: The name of the member's big

    + `pledge_semester`: A semester name (i.e., "Fall 2017" or "Spring 2017")

#. Enter `snutree -o <OUTPUT_NAME>.pdf <CSV_NAME>`

Advanced Usage
==============

Member Formats
--------------

There are other member schemas available under `snutree.member`. Additional,
custom, member schemas can be created by writing a Python module with a
function called `dicts_to_members(dicts)` that takes a list of dictionaries and
converts it into a list of `snutree.tree.Member` objects. To use a custom
module, run:

    snutree -m <MEMBER_FORMAT>[.py] -o <OUTPUT_NAME>.pdf <CSV_NAME>

SQL
---

Instead of using CSVs, one can also use queries to a SQL database. To do so,
include YAML files as inputs instead. The contents of each files should be:

~~~yaml
mysql:
  host: <SQL_HOST_IP>       # or 127.0.0.1 if using ssh
  port: <SQL_HOST_PORT>
  user: <SQL_USER>
  passwd: <SQL_USER_PASSWD>
  db: <SQL_DB_MAME>

# Optional
ssh:
  host: <REMOTE_HOST>
  port: <SSH_PORT>
  user: <SSH_USER>
  public_key: <SSH_PUBLIC_KEY_FILENAME>

query: <SQL_QUERY>

~~~

Data Flow
=========

~~~
snutree.readers:
    list: csv, sql, dot
    entry: get_table(stream)
    input: file streams
    output: list of dictionaries
snutree.member:
    list: basic, chapter, keyed, sigmanu
    entry: dicts_to_members(dicts)
    input: list of dictionaries
    output: list of Member objects
snutree.tree:
    list: FamilyTree
    entry: FamilyTree(members, settings)
    input: list of Member objects
    output: FamilyTree object
~~~

The tree object then can run its to_dot_graph() method to convert into a DOT
code representation, which can run to_dot() to convert into a string
representation, and finally:

~~~
snutree.???
    list: pdf, dot
    entry: write_output(dotcode, output_path)
    input: DOT code and path to output to
    output: desired output format
~~~

