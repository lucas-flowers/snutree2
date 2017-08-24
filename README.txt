Introduction
============

Some Greek-letter organizations assign big brothers or big sisters ("bigs") to
new members ("littles"). This program visualizes such relationships as a family
tree, using Graphviz.

Usage
=====

Command Line
------------

Basic Usage
~~~~~~~~~~~

The simplest usage of ``snutree`` is:

.. code:: bash

    snutree -o output.pdf input1.csv input2.csv ...

In this example, the CSV should have columns called ``name``, ``big_name``, and
``semester`` where ``semester``\s are strings starting with "Fall" or "Spring"
and ending with a year (e.g., "Fall 2014" or "Spring 1956"). With this input,
``snutree`` will append all the input tables together, convert them into a
tree, and output the tree using Graphviz. Each member will be put on a row
representing the semester they joined.

Changing Schemas
~~~~~~~~~~~~~~~~

The (``name``, ``big_name``, ``semester``) headers consist of the
"basic" schema. There are a few other schemas available. They are:

+---------+------------------------------------------------------------------+
| Schema  | Headers                                                          |
+=========+==================================================================+
| basic   | name, big\_name, semester                                        |
+---------+------------------------------------------------------------------+
| keyed   | id, name, big\_id, semester                                      |
+---------+------------------------------------------------------------------+
| chapter | child, parent, founded                                           |
+---------+------------------------------------------------------------------+
| sigmanu | badge, first\_name, preferred\_name, last\_name, big\_badge,     |
|         | status, semester, affiliations                                   |
+---------+------------------------------------------------------------------+

Changing schemas can be done with the ``--schema`` option. For example, this
will print the DOT source code of a family tree of chapters to the terminal:

.. code:: bash

    snutree --schema chapter chapters.csv

A custom Python module may be used as a schema:

.. code:: bash

    snutree --schema /home/example/custom.py input.csv

Custom schema modules should validate the tables themselves and turn them into
an internal format ``snutree`` can read.

SQL Queries
~~~~~~~~~~~

Input files can also be SQL queries. This will run the query in ``query.sql``
on the database described in ``config.yaml`` and save the resulting tree to
``output.pdf``:

.. code:: bash

    snutree --config config.yaml -o output.pdf query.sql

For a SQL query, a YAML configuration file with appropriate authentication
options must be provided. Here is an example of the contents of such a file:

.. code:: yaml

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
          private_key: '/home/example/.ssh/id_rsa'

Note that the query must rename the column headers to match the schema used.

Command Line Summary
~~~~~~~~~~~~~~~~~~~~

.. code::

    Usage: snutree.py [OPTIONS] [INPUT_FILES]...

    Options:
      --version                       Show the version and exit.
      -S, --seed INTEGER              Seed for the random number generator. Used
                                      to move tree nodes around in a repeatable
                                      way.
      -t, --to EXT                    File format for output. Must be supported by
                                      the writer. Defaults to the output's file
                                      extension if it is known or 'dot' if it is
                                      unknown.
      -w, --writer [dot|stats|MODULE]
                                      Writing module. May be the path to a custom
                                      Python module. If no module is given, one is
                                      guessed based on the output filetype.
      -m, --schema [basic|chapter|keyed|sigmanu|MODULE]
                                      Member table schema. May be the path to a
                                      custom Python module. Defaults to 'basic'.
      -f, --from [csv|dot|sql]        File format for input coming through stdin.
                                      Assumed to be 'csv' if not given.
      -c, --config PATH               Program configuration files
      -o, --output PATH               Instead of writing DOT code to stdout, send
                                      output to the file given.
      -l, --log PATH                  Log file path.
      -q, --quiet                     Only print errors to stderr; no warnings.
      -d, --debug                     Print debug information to stderr.
      -v, --verbose                   Print information to stderr.
      --help                          Show this message and exit.


GUI
---

The ``snutree`` package also includes a simple GUI called ``snutree-qt``. The
GUI can take multiple input files of any supported format, pick schemas, output
to PDF, and choose a seed for the random number generator.

Installation
============

First, install the following applications for your operating system and ensure
they are in your PATH:

  - Python >=3.6

  - `Graphviz <http://graphviz.org>`_ (be sure that ``dot`` is in your PATH)

Then install ``snutree`` and its Python dependencies with Python's ``pip``:

.. code:: bash

    pip install snutree

Optional Dependencies
---------------------

Use ``pip`` to install these packages for optional features:

    - ``pyqt5``: Use the GUI

    - ``mysqlclient``: Allow reading from MySQL databases

        - ``sshtunnel``: Allow tunneling SQL queries through ssh

    - ``pydotplus``: Allow reading data from DOT files (experimental)

Configuration
=============

All configuration is done in YAML (or JSON) files. In the terminal, these files
can be included with ``--config`` flags. Configuration files listed later
override those that came earlier and command line options override all
configuration files.

Below are all of the available options along with descriptions in the comments
and default values where applicable.

General
-------

.. code:: yaml

    readers: # reader module configuration
      stdin: # standard input reader configuration
        filetype: csv # type of files coming from stdin
      <reader1>:
      <reader2>: ...
    schema: # members schema module configuration
      name: basic # member schema module name
    writer: # writer module configuration
      filetype: # output filetype
      name: dot # writer module name
      file: None # output file name
    seed: 71 # random number generator seed

Readers
-------

SQL Reader
~~~~~~~~~~

If SSH is used, the SQL hostname should be ``127.0.0.1``.

.. code:: yaml

    host: 127.0.0.1 # SQL server hostname
    user: root # SQL username
    passwd: # SQL user password
    port: 3306 # SQL server port
    db: # SQL database name
    ssh: # credentials to encrypt SQL connection with SSH
      host: # SSH server hostname
      port: 22 # SSH server port
      user: # SSH username
      private_key: # SSH private keyfile path

Schemas
-------

Sigma Nu Schema
~~~~~~~~~~~~~~~

.. code:: yaml

    name: sigmanu
    chapter: # the chapter whose family tree will be generated

Writers
-------

DOT Writer
~~~~~~~~~~

See `Graphviz's documentation <http://graphviz.org/content/attrs>`_ for
available DOT attributes.

.. code:: yaml

    name: dot # writer name
    filetype: # output filetype
    file: # output file name
    ranks: True # enable ranks
    custom_edges: True # enable custom edges
    custom_nodes: True # enable custom nodes
    no_singletons: True # delete member nodes with neither parent nor child nodes
    colors: True # add color to member nodes
    unknowns: True # add parent nodes to members without any
    warn_rank: None # if no_singletons=True, singletons with rank>=warn_rank trigger warnings when dropped
    defaults: # default Graphviz attributes
      graph: # defaults for Graphviz graphs
        all:
          <name1>: <value1>
          <name2>: ...
      node: # defaults for Graphviz nodes
        all: # all nodes
          <name1>: <value1>
          <name2>: ...
        rank: # rank nodes
          <name1>: <value1>
          <name2>: ...
        unknown: # nodes of unknown parents
          <name1>: <value1>
          <name2>: ...
        member: # member nodes
          <name1>: <value1>
          <name2>: ...
      edge: # defaults for Graphviz edges
        all: # all edges
          <name1>: <value1>
          <name2>: ...
        rank: # edges between rank nodes
          <name1>: <value1>
          <name2>: ...
        unknown: # edges coming from unknown parents
          <name1>: <value1>
          <name2>: ...
    family_colors: # map of member keys to Graphviz colors
      <key1>: <color1>
      <key2>: ...
    nodes: # custom Graphviz nodes
      <key1>:
        rank: # the rank (i.e., year, semester, etc.) the node is in
        attributes: # Graphviz node attributes
          <name1>: <value1>
          <name2>: ...
      <key2>: ...
    edges: # a list of custom Graphviz edges
      - # edge1
        nodes: # keys of nodes connected by this edge
          - # key1
          - ...
        attributes: # Graphviz edge attributes
          <name1>: <value1>
          <name2>: ...
      - ...

Versioning
==========

This project loosely uses `Semantic Versioning <http://semver.org/>`_.

License
=======

This project is licensed under
`GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>`_.

.. vim: filetype=rst
