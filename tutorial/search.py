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
# ---
#
# To get started: consult [start](start.ipynb)
#
# ---
#
# # Search Introduction
#
# *Search* in Text-Fabric is a template based way of looking for structural patterns in your dataset.
#
# It is inspired by the idea of
# [topographic query](http://books.google.nl/books?id=9ggOBRz1dO4C).
#
# Within Text-Fabric we have the unique possibility to combine the ease of formulating search templates for
# complicated patterns with the power of programmatically processing the results.
#
# This notebook will show you how to get up and running.
#
# ## Alternative for hand-coding
#
# Search is a powerful feature for a wide range of purposes.
#
# Quite a bit of the implementation work has been dedicated to optimize performance.
# Yet I do not pretend to have found optimal strategies for all
# possible search templates.
# Some search tasks may turn out to be somewhat costly or even very costly.
#
# That being said, I think search might turn out helpful in many cases,
# especially by reducing the amount of hand-coding needed to work with special subsets of your data.
#
# ## Easy command
#
# Search is as simple as saying (just an example)
#
# ```python
# results = A.search(template)
# A.show(results)
# ```
#
# See all ins and outs in the
# [search template docs](https://annotation.github.io/text-fabric/tf/about/searchusage.html).

# %load_ext autoreload
# %autoreload 2

from tf.app import use

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# # Basic search command
#
# We start with the most simple form of issuing a query.
# Let's look for the numerals with a repeat greater than 3.
# We also want to show the words in which they occur.
#
# All work involved in searching takes place under the hood.

query = """
word
  sign type=numeral repeat>3
"""
results = A.search(query)

A.table(results, end=10)

# We can show them in unicode representation as well:

A.table(results, end=10, fmt="text-orig-unicode")

# The hyperlinks take us all to the CDLI archival page of the document (tablet) in question.
#
# Note that we can choose start and/or end points in the results list.

A.table(results, start=500, end=503, fmt="text-orig-rich")

# We can show the results more fully with `show()`.
#
# That gives us pretty displays of tablet lines with the results highlighted.

A.show(results, end=3)

# # Condense results
#
# There are two fundamentally different ways of presenting the results: condensed and uncondensed.
#
# In **uncondensed** view, all results are listed individually.
# You can keep track of which parts belong to which results.
# The display can become unwieldy.
#
# This is the default view, because it is the straightest, most logical, answer to your query.
#
# In **condensed** view all nodes of all results are grouped in containers first (e.g. verses), and then presented
# container by container.
# You loose the information of what parts belong to what result.
#
# As an example of is the difference, we look for all numerals.

query = """
% we choose a tablet with several numerals
document pnumber=P510556
  sign type=numeral repeat>3
"""

# Note that you can have comments in a search template. Comment lines start with a `%`.

results = A.search(query)
A.table(results, end=10)

# Let's expand the results display:

A.show(results, end=2, skipCols="1")

# As you see, the results are listed per result tuple, even if they occur all in the same verse.
# This way you can keep track of what exactly belongs to each result.
#
# Now in condensed mode:

A.show(results, condensed=True, withNodes=True)

# The last line has two results, and both results are highlighted in the same line display.
#
# We can modify the container in which we see our results.
#
# By default, it is `line`, but we can make it `face` as well:

A.show(results, end=2, condensed=True, condenseType="face")

# We now see the the displays of two faces, one with two numerals in it and one with three.

# # Custom highlighting
#
# Let us make a new search where we look for two different things in the same line.
#
# We can apply different highlight colors to different parts of the result.
# The signs in the pair are member 0 and 1 of the result tuples.
# The members that we do not map, will not be highlighted.
# The members that we map to the empty string will be highlighted with the default color.
#
# **NB:** Choose your colors from the
# [CSS specification](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value).

query = """
line
  sign missing=1
  sign question=1
  sign damage=1
"""

results = A.search(query)
A.table(results, end=10, baseTypes="sign")

A.table(
    results,
    end=10,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

A.show(results, end=5, colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"})

# Color mapping works best for uncondensed results. If you condense results, some nodes may occupy
# different positions in different results. It is unpredictable which color will be used
# for such nodes:

A.show(
    results,
    condensed=True,
    end=5,
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# You can specify to what container you want to condense. By default, everything is condensed to lines.
#
# Let's change that to faces.
# Note that the `end` parameter counts the number of faces now.

A.show(
    results,
    end=2,
    condensed=True,
    condenseType="face",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# # Constraining order
# You can stipulate an order on the things in your template.
# You only have to put a relational operator between them.
# Say we want only results where the damage follows the missing.

query = """
line
  sign question=1
  sign missing=1
  < sign damage=1
"""

results = A.search(query)
A.table(results, end=10, baseTypes="sign")

# We can also require the things to be adjacent.

query = """
line
  sign question=1
  sign missing=1
  <: sign damage=1
"""

results = A.search(query)
A.table(results, end=10, baseTypes="sign")
A.show(
    results,
    end=10,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# Finally, we make the three things fully adjacent in fixed order:

query = """
line
  sign question=1
  <: sign missing=1
  <: sign damage=1
"""

results = A.search(query)
A.table(results, end=10, baseTypes="sign")
A.show(results, end=10, colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"})

# # Custom feature display
#
# We would like to see the original atf and the flags for signs.
# The way to do that, is to perform a `A.prettySetup(features)` first.
#
# We concentrate on one specific result.

A.displaySetup(extraFeatures="atf flags")

A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# The features without meaningful values have been left out. We can also change that by passing a set of values
# we think are not meaningful. The default set is
#
# ```python
# {None, 'NA', 'none', 'unknown'}
# ```

A.displaySetup(noneValues=set())
A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# This makes clear that it is convenient to keep `None` in the `noneValues`:

A.displaySetup(noneValues={None})
A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# We can even choose to suppress other values, e.g. the value 1.
#
# That will remove all the features such as `question`, `missing`.

A.displaySetup(noneValues={None, "NA", "unknown", 1})
A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# In the rest of the notebook we stick to our normal setup, so we reset the extra features.

A.displayReset()
A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# # Features from queries
#
# In earlier displays we saw the *types* of signs, because the query mentioned it.
#
# Suppose we want to display the type also here, then we can modify the query by mentioning the feature `type`.
#
# But we do not want to impose extra limitations, so we say `type*`, meaning: no conditions on type whatsoever.

query = """
line
  sign question=1 type*
  <: sign missing=1
  <: sign damage=1
"""

results = A.search(query)
A.show(
    results, start=4, end=4, colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"}
)

# We do not see the features, because they are `sign` features, and our display stops at the `word` level.
# But we can improve on that:

A.show(
    results,
    start=4,
    end=4,
    baseTypes="sign",
    colorMap={0: "", 2: "cyan", 3: "magenta", 4: "lightsalmon"},
)

# # Show your own tuples
#
# So far we have `show()`n the results of searches.
# But you can also construct your own tuples and show them.
#
# Whereas you can use search to get a pretty good approximation of what you want, most of the times
# you do not arrive precisely at your destination.
#
# Here is an example where we use search to come close, and then work our way to produce the end result.
#
# ## More missing than damaged
#
# We look for lines that have more missing signs than damaged signs.
#
# In our search templates we cannot formulate that a feature has different values on two nodes in the template.
# We could spell out all possible combinations of values and make a search template for each of them,
# but that is needlessly complex.
#
# Let's first use search to find all clauses containing missing and damaged signs.

query = """
line
  sign missing
  sign damage
"""
results = A.search(query)

# Now the hand coding begins. We are going to extract the tuples we want.

lines = {}
for (l, m, d) in results:
    lines.setdefault(l, (set(), set()))
    lines[l][0].add(m)
    lines[l][1].add(d)
print(f"{len(lines)} lines")

# Now we have all lines with both missing and damaged signs, without duplicates.
#
# For each line we have a set with its missing signs and one with its damaged signs.
#
# We filter in order to retain the lines with more missing than damaged signs.
# We put all missing signs in one big set and all damaged signs in one big set.

# +
answer = []
missing = set()
damage = set()

for (l, (m, d)) in lines.items():
    if len(m) > len(d):
        answer.append((l, *m, *d))
        missing |= m
        damage |= d
len(answer)
# -

answer[0]

# We are going to make a dictionary of highligts: one color for the missing signs and one for the damaged.

highlights = {}
colorM = "lightsalmon"
colorD = "mediumaquamarine"
for s in missing:
    highlights[s] = colorM
for s in damage:
    highlights[s] = colorD

# And now we can show them:

A.table(answer, start=1, end=10, highlights=highlights)

# As you see, you have total control.

# ---
#
# All chapters:
#
# * **[start](start.ipynb)** become an expert in creating pretty displays of your text structures
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **search** turbo charge your hand-coding with search templates
# * **[exportExcel](exportExcel.ipynb)** make tailor-made spreadsheets out of your results
# * **[share](share.ipynb)** draw in other people's data and let them use yours
# * **[similarLines](similarLines.ipynb)** spot the similarities between lines
#
# ---
#
# See the [cookbook](cookbook) for recipes for small, concrete tasks.
#
# CC-BY Dirk Roorda
