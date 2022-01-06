# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# <img align="right" src="images/tf.png" width="128"/>
# <img align="right" src="images/ninologo.png" width="128"/>
# <img align="right" src="images/dans.png" width="128"/>
#
# # Tutorial
#
# This notebook gets you started with using
# [Text-Fabric](https://annotation.github.io/text-fabric/) for coding in the Old-Babylonian Letter corpus (cuneiform).
#
# Familiarity with the underlying
# [data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html)
# is recommended.

# ## Installing Text-Fabric
#
# ### Python
#
# You need to have Python on your system. Most systems have it out of the box,
# but alas, that is python2 and we need at least python **3.6**.
#
# Install it from [python.org](https://www.python.org) or from
# [Anaconda](https://www.anaconda.com/download).
#
# ### TF itself
#
# ```
# pip3 install text-fabric
# ```
#
# ### Jupyter notebook
#
# You need [Jupyter](http://jupyter.org).
#
# If it is not already installed:
#
# ```
# pip3 install jupyter
# ```

# ## Tip
# If you cloned the repository containing this tutorial,
# first copy its parent directory to somewhere outside your clone of the repo,
# before computing with this it.
#
# If you pull changes from the repository later, it will not conflict with
# your computations.
#
# Where you put your tutorial directory is up to you.
# It will work from any directory.

# ## Old Babylonian data
#
# Text-Fabric will fetch the data set for you from the newest github release binaries.
#
# The data will be stored in the `text-fabric-data` in your home directory.

# # Features
# The data of the corpus is organized in features.
# They are *columns* of data.
# Think of the corpus as a gigantic spreadsheet, where row 1 corresponds to the
# first sign, row 2 to the second sign, and so on, for all 200,000 signs.
#
# The information which reading each sign has, constitutes a column in that spreadsheet.
# The Old Babylonian corpus contains nearly 60 columns, not only for the signs, but also for thousands of other
# textual objects, such as clusters, lines, columns, faces, documents.
#
# Instead of putting that information in one big table, the data is organized in separate columns.
# We call those columns **features**.

# %load_ext autoreload
# %autoreload 2

import os
import collections

# # Incantation
#
# The simplest way to get going is by this *incantation*:

from tf.app import use

# For the very last version, use `hot`.
#
# For the latest release, use `latest`.
#
# If you have cloned the repos (TF app and data), use `clone`.
#
# If you do not want/need to upgrade, leave out the checkout specifiers.

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian:hot', checkout="hot", hoist=globals())
# A = use('oldbabylonian:latest', checkout="latest", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# You can see which features have been loaded, and if you click on a feature name, you find its documentation.
# If you hover over a name, you see where the feature is located on your system.

# ## API
#
# The result of the incantation is that we have a bunch of special variables at our disposal
# that give us access to the text and data of the corpus.
#
# At this point it is helpful to throw a quick glance at the text-fabric API documentation
# (see the links under **API Members** above).
#
# The most essential thing for now is that we can use `F` to access the data in the features
# we've loaded.
# But there is more, such as `N`, which helps us to walk over the text, as we see in a minute.
#
# The **API members** above show you exactly which new names have been inserted in your namespace.
# If you click on these names, you go to the API documentation for them.

# ## Search
# Text-Fabric contains a flexible search engine, that does not only work for the data,
# of this corpus, but also for other corpora and data that you add to corpora.
#
# **Search is the quickest way to come up-to-speed with your data, without too much programming.**
#
# Jump to the dedicated [search](search.ipynb) search tutorial first, to whet your appetite.
#
# The real power of search lies in the fact that it is integrated in a programming environment.
# You can use programming to:
#
# * compose dynamic queries
# * process query results
#
# Therefore, the rest of this tutorial is still important when you want to tap that power.
# If you continue here, you learn all the basics of data-navigation with Text-Fabric.

# # Counting
#
# In order to get acquainted with the data, we start with the simple task of counting.
#
# ## Count all nodes
# We use the
# [`N.walk()` generator](https://annotation.github.io/text-fabric/tf/core/nodes.html#tf.core.nodes.Nodes.walk)
# to walk through the nodes.
#
# We compared the TF data to a gigantic spreadsheet, where the rows correspond to the signs.
# In Text-Fabric, we call the rows `slots`, because they are the textual positions that can be filled with signs.
#
# We also mentioned that there are also other textual objects.
# They are the clusters, lines, faces and documents.
# They also correspond to rows in the big spreadsheet.
#
# In Text-Fabric we call all these rows *nodes*, and the `N()` generator
# carries us through those nodes in the textual order.
#
# Just one extra thing: the `info` statements generate timed messages.
# If you use them instead of `print` you'll get a sense of the amount of time that
# the various processing steps typically need.

# +
A.indent(reset=True)
A.info("Counting nodes ...")

i = 0
for n in N.walk():
    i += 1

A.info("{} nodes".format(i))
# -

# Here you see it: over 300,000 nodes.

# ## What are those nodes?
# Every node has a type, like sign, or line, face.
# But what exactly are they?
#
# Text-Fabric has two special features, `otype` and `oslots`, that must occur in every Text-Fabric data set.
# `otype` tells you for each node its type, and you can ask for the number of `slot`s in the text.
#
# Here we go!

F.otype.slotType

F.otype.maxSlot

F.otype.maxNode

F.otype.all

C.levels.data

# This is interesting: above you see all the textual objects, with the average size of their objects,
# the node where they start, and the node where they end.

# ## Count individual object types
# This is an intuitive way to count the number of nodes in each type.
# Note in passing, how we use the `indent` in conjunction with `info` to produce neat timed
# and indented progress messages.

# +
A.indent(reset=True)
A.info("counting objects ...")

for otype in F.otype.all:
    i = 0

    A.indent(level=1, reset=True)

    for n in F.otype.s(otype):
        i += 1

    A.info("{:>7} {}s".format(i, otype))

A.indent(level=0)
A.info("Done")
# -

# # Viewing textual objects
#
# You can use the A API (the extra power) to display cuneiform text.
#
# See the [display](display.ipynb) tutorial.

# # Feature statistics
#
# `F`
# gives access to all features.
# Every feature has a method
# `freqList()`
# to generate a frequency list of its values, higher frequencies first.
# Here are the repeats of numerals (the `-1` comes from a `n(rrr)`:

F.repeat.freqList()

# Signs have types and clusters have types. We can count them separately:

F.type.freqList("cluster")

F.type.freqList("sign")

# Finally, the flags:

F.flags.freqList()

# # Word matters
#
# ## Top 20 frequent words
#
# We represent words by their essential symbols, collected in the feature *sym* (which also exists for signs).

for (w, amount) in F.sym.freqList("word")[0:20]:
    print(f"{amount:>5} {w}")

# ## Word distribution
#
# Let's do a bit more fancy word stuff.
#
# ### Hapaxes
#
# A hapax can be found by picking the words with frequency 1
#
# We print 20 hapaxes.

for w in [w for (w, amount) in F.sym.freqList("word") if amount == 1][0:20]:
    print(f'"{w}"')

# ### Small occurrence base
#
# The occurrence base of a word are the documents in which occurs.
#
# We compute the occurrence base of each word.

# +
occurrenceBase = collections.defaultdict(set)

for w in F.otype.s("word"):
    pNum = T.sectionFromNode(w)[0]
    occurrenceBase[F.sym.v(w)].add(pNum)
# -

# An overview of how many words have how big occurrence bases:

# +
occurrenceSize = collections.Counter()

for (w, pNums) in occurrenceBase.items():
    occurrenceSize[len(pNums)] += 1

occurrenceSize = sorted(
    occurrenceSize.items(),
    key=lambda x: (-x[1], x[0]),
)

for (size, amount) in occurrenceSize[0:10]:
    print(f"base size {size:>4} : {amount:>5} words")
print("...")
for (size, amount) in occurrenceSize[-10:]:
    print(f"base size {size:>4} : {amount:>5} words")
# -

# Let's give the predicate *private* to those words whose occurrence base is a single document.

privates = {w for (w, base) in occurrenceBase.items() if len(base) == 1}
len(privates)

# ### Peculiarity of documents
#
# As a final exercise with words, lets make a list of all documents, and show their
#
# * total number of words
# * number of private words
# * the percentage of private words: a measure of the peculiarity of the document

# +
docList = []

empty = set()
ordinary = set()

for d in F.otype.s("document"):
    pNum = T.documentName(d)
    words = {F.sym.v(w) for w in L.d(d, otype="word")}
    a = len(words)
    if not a:
        empty.add(pNum)
        continue
    o = len({w for w in words if w in privates})
    if not o:
        ordinary.add(pNum)
        continue
    p = 100 * o / a
    docList.append((pNum, a, o, p))

docList = sorted(docList, key=lambda e: (-e[3], -e[1], e[0]))

print(f"Found {len(empty):>4} empty documents")
print(f"Found {len(ordinary):>4} ordinary documents (i.e. without private words)")

# +
print(
    "{:<20}{:>5}{:>5}{:>5}\n{}".format(
        "document",
        "#all",
        "#own",
        "%own",
        "-" * 35,
    )
)

for x in docList[0:20]:
    print("{:<20} {:>4} {:>4} {:>4.1f}%".format(*x))
print("...")
for x in docList[-20:]:
    print("{:<20} {:>4} {:>4} {:>4.1f}%".format(*x))
# -

# # Locality API
# We travel upwards and downwards, forwards and backwards through the nodes.
# The Locality-API (`L`) provides functions: `u()` for going up, and `d()` for going down,
# `n()` for going to next nodes and `p()` for going to previous nodes.
#
# These directions are indirect notions: nodes are just numbers, but by means of the
# `oslots` feature they are linked to slots. One node *contains* an other node, if the one is linked to a set of slots that contains the set of slots that the other is linked to.
# And one if next or previous to an other, if its slots follow or precede the slots of the other one.
#
# `L.u(node)` **Up** is going to nodes that embed `node`.
#
# `L.d(node)` **Down** is the opposite direction, to those that are contained in `node`.
#
# `L.n(node)` **Next** are the next *adjacent* nodes, i.e. nodes whose first slot comes immediately after the last slot of `node`.
#
# `L.p(node)` **Previous** are the previous *adjacent* nodes, i.e. nodes whose last slot comes immediately before the first slot of `node`.
#
# All these functions yield nodes of all possible otypes.
# By passing an optional parameter, you can restrict the results to nodes of that type.
#
# The result are ordered according to the order of things in the text.
#
# The functions return always a tuple, even if there is just one node in the result.
#
# ## Going up
# We go from the first word to the document it contains.
# Note the `[0]` at the end. You expect one document, yet `L` returns a tuple.
# To get the only element of that tuple, you need to do that `[0]`.
#
# If you are like me, you keep forgetting it, and that will lead to weird error messages later on.

firstDoc = L.u(1, otype="document")[0]
print(firstDoc)

# And let's see all the containing objects of sign 3:

s = 3
for otype in F.otype.all:
    if otype == F.otype.slotType:
        continue
    up = L.u(s, otype=otype)
    upNode = "x" if len(up) == 0 else up[0]
    print("sign {} is contained in {} {}".format(s, otype, upNode))

# ## Going next
# Let's go to the next nodes of the first document.

afterFirstDoc = L.n(firstDoc)
for n in afterFirstDoc:
    print(
        "{:>7}: {:<13} first slot={:<6}, last slot={:<6}".format(
            n,
            F.otype.v(n),
            E.oslots.s(n)[0],
            E.oslots.s(n)[-1],
        )
    )
secondDoc = L.n(firstDoc, otype="document")[0]

# ## Going previous
#
# And let's see what is right before the second document.

for n in L.p(secondDoc):
    print(
        "{:>7}: {:<13} first slot={:<6}, last slot={:<6}".format(
            n,
            F.otype.v(n),
            E.oslots.s(n)[0],
            E.oslots.s(n)[-1],
        )
    )

# ## Going down

# We go to the faces of the first document, and just count them.

faces = L.d(firstDoc, otype="face")
print(len(faces))

# ## The first line
# We pick two nodes and explore what is above and below them:
# the first line and the first word.

for n in [
    F.otype.s("word")[0],
    F.otype.s("line")[0],
]:
    A.indent(level=0)
    A.info("Node {}".format(n), tm=False)
    A.indent(level=1)
    A.info("UP", tm=False)
    A.indent(level=2)
    A.info("\n".join(["{:<15} {}".format(u, F.otype.v(u)) for u in L.u(n)]), tm=False)
    A.indent(level=1)
    A.info("DOWN", tm=False)
    A.indent(level=2)
    A.info("\n".join(["{:<15} {}".format(u, F.otype.v(u)) for u in L.d(n)]), tm=False)
A.indent(level=0)
A.info("Done", tm=False)

# # Text API
#
# So far, we have mainly seen nodes and their numbers, and the names of node types.
# You would almost forget that we are dealing with text.
# So let's try to see some text.
#
# In the same way as `F` gives access to feature data,
# `T` gives access to the text.
# That is also feature data, but you can tell Text-Fabric which features are specifically
# carrying the text, and in return Text-Fabric offers you
# a Text API: `T`.
#
# ## Formats
# Cuneiform text can be represented in a number of ways:
#
# * original ATF, with bracketings and flags
# * essential symbols: readings and graphemes, repeats and fractions (of numerals), no flags, no clusterings
# * unicode symbols
#
# If you wonder where the information about text formats is stored:
# not in the program text-fabric, but in the data set.
# It has a feature `otext`, which specifies the formats and which features
# must be used to produce them. `otext` is the third special feature in a TF data set,
# next to `otype` and `oslots`.
# It is an optional feature.
# If it is absent, there will be no `T` API.
#
# Here is a list of all available formats in this data set.

sorted(T.formats)

# ## Using the formats
#
# The ` T.text()` function is central to get text representations of nodes. Its most basic usage is
#
# ```python
# T.text(nodes, fmt=fmt)
# ```
# where `nodes` is a list or iterable of nodes, usually word nodes, and `fmt` is the name of a format.
# If you leave out `fmt`, the default `text-orig-full` is chosen.
#
# The result is the text in that format for all nodes specified:

T.text([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], fmt="text-orig-plain")

# There is also another usage of this function:
#
# ```python
# T.text(node, fmt=fmt)
# ```
#
# where `node` is a single node.
# In this case, the default format is *ntype*`-orig-full` where *ntype* is the type of `node`.
#
# If the format is defined in the corpus, it will be used. Otherwise, the word nodes contained in `node` will be looked up
# and represented with the default format `text-orig-full`.
#
# In this way we can sensibly represent a lot of different nodes, such as documents, faces, lines, clusters, words and signs.
#
# We compose a set of example nodes and run `T.text` on them:

exampleNodes = [
    F.otype.s("sign")[0],
    F.otype.s("word")[0],
    F.otype.s("cluster")[0],
    F.otype.s("line")[0],
    F.otype.s("face")[0],
    F.otype.s("document")[0],
]
exampleNodes

for n in exampleNodes:
    print(f"This is {F.otype.v(n)} {n}:")
    print(T.text(n))
    print("")

# ## Using the formats
# Now let's use those formats to print out the first line in this corpus.
#
# Note that only the formats starting with `text-` are usable for this.
#
# For the `layout-` formats, see [display](display.ipynb).

for fmt in sorted(T.formats):
    if fmt.startswith("text-"):
        print("{}:\n\t{}".format(fmt, T.text(range(1, 12), fmt=fmt)))

# If we do not specify a format, the **default** format is used (`text-orig-full`).

T.text(range(1, 12))

firstLine = F.otype.s("line")[0]
T.text(firstLine)

T.text(firstLine, fmt="text-orig-unicode")

# The important things to remember are:
#
# * you can supply a list of slot nodes and get them represented in all formats
# * you can get non-slot nodes `n` in default format by `T.text(n)`
# * you can get non-slot nodes `n` in other formats by `T.text(n, fmt=fmt, descend=True)`

# ## Whole text in all formats in just 2 seconds
# Part of the pleasure of working with computers is that they can crunch massive amounts of data.
# The text of the Old Babylonian Letters is a piece of cake.
#
# It takes just ten seconds to have that cake and eat it.
# In nearly a dozen formats.

# +
A.indent(reset=True)
A.info("writing plain text of all letters in all text formats")

text = collections.defaultdict(list)

for ln in F.otype.s("line"):
    for fmt in sorted(T.formats):
        if fmt.startswith("text-"):
            text[fmt].append(T.text(ln, fmt=fmt, descend=True))

A.info("done {} formats".format(len(text)))

for fmt in sorted(text):
    print("{}\n{}\n".format(fmt, "\n".join(text[fmt][0:5])))
# -

# ### The full plain text
# We write all formats to file, in your `Downloads` folder.

for fmt in T.formats:
    if fmt.startswith("text-"):
        with open(os.path.expanduser(f"~/Downloads/{fmt}.txt"), "w") as f:
            f.write("\n".join(text[fmt]))

# ## Sections
#
# A section in the letter corpus is a document, a face or a line.
# Knowledge of sections is not baked into Text-Fabric.
# The config feature `otext.tf` may specify three section levels, and tell
# what the corresponding node types and features are.
#
# From that knowledge it can construct mappings from nodes to sections, e.g. from line
# nodes to tuples of the form:
#
#     (p-number, face specifier, line number)
#
# You can get the section of a node as a tuple of relevant document, face, and line nodes.
# Or you can get it as a passage label, a string.
#
# You can ask for the passage corresponding to the first slot of a node, or the one corresponding to the last slot.
#
# If you are dealing with document and face nodes, you can ask to fill out the line and face parts as well.
#
# Here are examples of getting the section that corresponds to a node and vice versa.
#
# **NB:** `sectionFromNode` always delivers a verse specification, either from the
# first slot belonging to that node, or, if `lastSlot`, from the last slot
# belonging to that node.

someNodes = (
    F.otype.s("sign")[100000],
    F.otype.s("word")[10000],
    F.otype.s("cluster")[5000],
    F.otype.s("line")[15000],
    F.otype.s("face")[1000],
    F.otype.s("document")[500],
)

for n in someNodes:
    nType = F.otype.v(n)
    d = f"{n:>7} {nType}"
    first = A.sectionStrFromNode(n)
    last = A.sectionStrFromNode(n, lastSlot=True, fillup=True)
    tup = (
        T.sectionTuple(n),
        T.sectionTuple(n, lastSlot=True, fillup=True),
    )
    print(f"{d:<16} - {first:<18} {last:<18} {tup}")

# # Clean caches
#
# Text-Fabric pre-computes data for you, so that it can be loaded faster.
# If the original data is updated, Text-Fabric detects it, and will recompute that data.
#
# But there are cases, when the algorithms of Text-Fabric have changed, without any changes in the data, that you might
# want to clear the cache of precomputed results.
#
# There are two ways to do that:
#
# * Locate the `.tf` directory of your dataset, and remove all `.tfx` files in it.
#   This might be a bit awkward to do, because the `.tf` directory is hidden on Unix-like systems.
# * Call `TF.clearCache()`, which does exactly the same.
#
# It is not handy to execute the following cell all the time, that's why I have commented it out.
# So if you really want to clear the cache, remove the comment sign below.

# +
# TF.clearCache()
# -

# # Next steps
#
# By now you have an impression how to compute around in the corpus.
# While this is still the beginning, I hope you already sense the power of unlimited programmatic access
# to all the bits and bytes in the data set.
#
# Here are a few directions for unleashing that power.
#
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **[search](search.ipynb)** turbo charge your hand-coding with search templates
# * **[exportExcel](exportExcel.ipynb)** make tailor-made spreadsheets out of your results
# * **[share](share.ipynb)** draw in other people's data and let them use yours
# * **[similarLines](similarLines.ipynb)** spot the similarities between lines
#
# ---
#
# See the [cookbook](cookbook) for recipes for small, concrete tasks.
#
# CC-BY Dirk Roorda
