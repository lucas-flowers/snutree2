=======
snutree
=======

.. contents::
    :backlinks: none

.. sectnum::

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

For a SQL query, a `YAML <http://www.yaml.org/start.html>`_ configuration file
with appropriate authentication options must be provided. Here is an example of
the contents of such a file:

.. code:: yaml

    readers:
      sql:
        host: '127.0.0.1'
        port: 3306
        user: 'root'
        passwd: 'secret'
        db: 'database_name'
        # Credentials for tunneling queries through SSH
        ssh:
          host: 'example.com'
          port: 22
          user: 'example'
          private_key: '/home/example/.ssh/id_rsa'

Note that the query must rename the column headers to match the schema used.

Command Line Summary
~~~~~~~~~~~~~~~~~~~~

.. code::

    usage: snutree [-h] [-o <path>] [-f <filetype>] [-t <filetype>] [-m <schema>]
                   [-w <writer>] [-c <path>] [-S <int>] [-l <path>] [-q] [-v] [-d]
                   [-V]
                   [<input> [<input> ...]]

    Visualizes big-little brother/sister relationships in Greek-letter
    organizations. Input file data is read from stdin and/or any provided
    positional <input> arguments. Each input <filetype> has a corresponding
    reader, which converts the file into a table of the given <schema> and adds it
    to the rest of the input data. The <schema> module then turns the the
    resulting table into a tree data structure. The tree is processed and finally
    written to the output <path> using the given <writer> and output <filetype>.
    Additional options can be provided in configuration files.

    positional arguments:
      <input>               an input file path or '-' for stdin; default is stdin

    optional arguments:
      -h, --help            show this help message and exit
      -o <path>, --output <path>
                            the output file; default is stdout
      -f <filetype>, --from <filetype>
                            expected filetype of stdin, which must be one of
                            {csv,dot,sql}; default is csv
      -t <filetype>, --to <filetype>
                            filetype of the output file, which must be supported
                            by the writer; default is the output file's extension
                            (if known) or 'dot'
      -m <schema>, --schema <schema>
                            member table schema, which must be in
                            {basic,chapter,keyed,sigmanu,*.py}; default is 'basic'
      -w <writer>, --writer <writer>
                            writer module, which must be in
                            {dot,stats,table,*.py}; default is a guess based on
                            the output file format
      -c <path>, --config <path>
                            configuration file <path(s)>; files listed earlier
                            override later ones
      -S <int>, --seed <int>
                            random number generator seed, for moving tree nodes
                            around in a repeatable way
      -l <path>, --log <path>
                            write logger output to the file at <path>
      -q, --quiet           write only errors to stderr; suppress warnings
      -v, --verbose         print more information to stderr
      -d, --debug           print debug-level information to stderr
      -V, --version         show program's version number and exit


GUI
---

There is also a simple GUI script called ``snutree-gui``. It is a simple
wrapper over the command-line version and implements most of the command-line
features.

Installation
============

With PIP
--------

These instructions are based on Ubuntu and Debian-based installations, but they
can be made to apply to any Unix-like system (including macOS) with what should
be minor modifications. (These instructions are also applicable to Windows,
though after less minor modifications.)

First, install Python (>=3.5), Python's ``pip`` package manager, and `Graphviz
<http://graphviz.org>`_:

.. code:: bash

    # apt install python3 python3-pip graphviz

At this point, ``python3``, ``pip3``, and ``dot`` should be in your PATH:

.. code:: bash

    $ python3 --version
    Python 3.X.X
    $ pip3 --version
    pip X.X.X from /path/to/python3/packages (python 3.5)
    $ dot -V
    dot - graphviz version X.XX.X (20XXXXXX.XXXX)

Now install ``snutree`` with:

.. code:: bash

    $ pip3 install --user snutree

This will install ``snutree`` and its required Python dependencies to your home
directory. Make sure that ``~/.local/bin`` is in your PATH. You might run
``pip`` without the ``--user`` flag to install it system-wide, but this will
require root.

Windows
-------

Since installation on Windows is less straightforward, Windows executables have
been compiled and are available `here
<https://github.com/lucas-flowers/snutree/releases>`_. After downloading the
executable, you must install Graphviz and add ``C:\Program Files
(x86)\GraphvizX.XX\bin`` (or equivalent) to your Windows PATH. You can now run
the command-line or GUI executables.

Optional Dependencies
---------------------

Use ``pip`` to install these packages for optional features:

- ``gooey``: Use the GUI version

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
    seed: 71 # random number generator seed
    writer: # writer module configuration
      file: None # output file name
      filetype: # output filetype
      name: None # writer module name

Readers
-------

SQL Reader
~~~~~~~~~~

.. code:: yaml

    db: # SQL database name
    host: 127.0.0.1 # SQL server hostname
    passwd: # SQL user password
    port: 3306 # SQL server port
    ssh: # credentials to encrypt SQL connection with SSH
      host: # SSH server hostname
      port: 22 # SSH server port
      private_key: # SSH private keyfile path
      user: # SSH username
    user: root # SQL username

Schemas
-------

Sigma Nu Schema
~~~~~~~~~~~~~~~

.. code:: yaml

    chapter: # the chapter whose family tree will be generated
    name: sigmanu

Writers
-------

DOT Writer
~~~~~~~~~~

See `Graphviz's documentation <http://graphviz.org/content/attrs>`_ for
available DOT attributes.

.. code:: yaml

    colors: True # add color to member nodes
    custom_edges: True # enable custom edges
    custom_nodes: True # enable custom nodes
    defaults: # default Graphviz attributes
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
      graph: # defaults for Graphviz graphs
        all:
          <name1>: <value1>
          <name2>: ...
      node: # defaults for Graphviz nodes
        all: # all nodes
          <name1>: <value1>
          <name2>: ...
        member: # member nodes
          <name1>: <value1>
          <name2>: ...
        rank: # rank nodes
          <name1>: <value1>
          <name2>: ...
        unknown: # nodes of unknown parents
          <name1>: <value1>
          <name2>: ...
    edges: # a list of custom Graphviz edges
      - # edge1
        attributes: # Graphviz edge attributes
          <name1>: <value1>
          <name2>: ...
        nodes: # keys of nodes connected by this edge
          - # key1
          - ...
      - ...
    family_colors: # map of member keys to Graphviz colors
      <key1>: <color1>
      <key2>: ...
    file: # output file name
    filetype: # output filetype
    name: dot # writer name
    no_singletons: True # delete member nodes with neither parent nor child nodes
    nodes: # custom Graphviz nodes
      <key1>:
        attributes: # Graphviz node attributes
          <name1>: <value1>
          <name2>: ...
        rank: # the rank (i.e., year, semester, etc.) the node is in
      <key2>: ...
    ranks: True # enable ranks
    unknowns: True # add parent nodes to members without any
    warn_rank: None # if no_singletons=True, singletons with rank>=warn_rank trigger warnings when dropped

Versioning
==========

This project loosely uses `Semantic Versioning <http://semver.org/>`_.

License
=======

This project is licensed under
`GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>`_.

