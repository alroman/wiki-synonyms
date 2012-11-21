wiki-synonyms
=============

## Description

A graphical representation of synonyms for technical terms.   Uses the Wikipedia API to
find a set of related technical terms and displays them as a graph.

For example: Binary tree would result in the set {AVL tree, AA tree, 2-3-4 tree, (a-b)-tree, 2-3 tree, ...}.
It's generally not easy to create these relationships with a thesaurus, so Wikipedia is used retrieve similar
terms.  Each term retrieved implies a Wikipedia entry, so potentially we can retrieve more synonyms for one
of the terms returned in the set.

## Techincal

This uses a mix of python and javascript to build the tree.  Python is used to query and parse the Wikipedia
results and 'Arbor.js' is used to create the graph representation.  Arbor.js powers the physics of the graph,
but the results are painted onscreen via Canvas.

I wrote a very simple python server to demo.  To view the demo run the server with

    python simple-server.py

Then open up: http://localhost:3000

