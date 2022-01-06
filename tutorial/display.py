# -*- coding: utf-8 -*-
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
# # Display
#
# We show the ins and outs of displaying cuneiform ATF transcriptions.

# %load_ext autoreload
# %autoreload 2

from tf.app import use

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# We pick an example face with which we illustrate many ways to represent cuneiform text.

# exampleFace = ('P509373', 'obverse')
# exampleFace = ('P292990', 'obverse')
exampleFace = ("P292987", "reverse")
f = T.nodeFromSection(exampleFace)
lines = L.d(f, otype="line")

# # Raw text
#
# The most basic way is to show the source material for each line, which is in the feature `srcLn`.
#
# This feature has been filled by mere copying the numbered lines from the CDLI ATF sources.

for ln in lines:
    print(F.srcLn.v(ln))

# # Text formats
#
# The TF API supports *text formats*. Text formats make selections and apply templates and styles based
# on the analysed features of the text. For example: a text-format may ignore flags or clusters, or
# format numerals in special ways.
#
# Text formats are not baked into TF, but they are defined in the feature `otext` of the corpus.
#
# Moreover, for this corpus a TF app has been build that defines additional text-formats.
#
# Whereas the formats defined in `otext` are strictly plain text formats, the formats
# defined in the app are able to use typographic styles to shape the text, such as bold, italic, colors, etc.
#
# Here is the list of all formats.

T.formats

# ## Plain text formats
#
# The formats whose names start with `text-` are the plain text formats.
#
# ### `text-orig-full`
#
# This format is really close to the ATF. It contains all original information.
#
# This is the default format. We do not have to specify it.

for ln in lines:
    print(ln, T.text(ln))
    A.plain(ln)

# The `plain()` function focuses on the *contents*, and instead of the line number, it gives a full specification
# of the location, linked to the online source on CDLI.
#
# But we can omit the locations:

for ln in lines:
    A.plain(ln, withPassage=False)

# ### `text-orig-plain`
#
# This is a somewhat reduced format. It omits all flags and bracketing constructs.
#
# For clarity, adjacent signs are separated with a `⁼` character.

for ln in lines:
    A.plain(ln, fmt="text-orig-plain")

# ### `text-orig-rich`
#
# This format is a bit prettier: instead of the strict ASCII encoding used by the CDLI archive, it uses
# characters with diacritics.
#
# There is no flag/cluster information in this representation.

for ln in lines:
    A.plain(ln, fmt="text-orig-rich")

# ### `text-orig-unicode`
#
# This format uses the Cuneiform Unicode characters.
#
# Numerals with repeats are represented by placing that many copies of the character in question.
#
# Readings that could not be found in the
# [mapping](https://github.com/Nino-cunei/oldbabylonian/blob/master/sources/writing/GeneratedSignList.json)
# we use, appear in latin characters.
#
# There is no flag/cluster information in this representation.

for ln in lines:
    A.plain(ln, fmt="text-orig-unicode")

# ## Styled text formats
#
# The formats whose names start with `layout-` are the styled text formats.
#
# ### `layout-orig-rich`
#
# This format looks like `text-orig-rich`, but now we re-introduce the flags and clusters by specific
# layout devices.
#
# See below for detailed examples.

for ln in lines:
    A.plain(ln, fmt="layout-orig-rich")

# ### `layout-orig-unicode`
#
# This format looks like `text-orig-unicode`, but now we re-introduce the flags and clusters by specific
# layout devices.
#
# See below for detailed examples.

for ln in lines:
    A.plain(ln, fmt="layout-orig-unicode")

# Here is the text of the face in each of the plain text formats, i.e. no additional HTML formatting is applied.

# # Pretty
#
# The ultimate of graphical display is by means of the `pretty()` function.
#
# This display is less useful for reading, but instead optimized for showing all information that you might
# wish for.
#
# It shows a base representation according to a text format of your choice
# (here we choose `layout-orig-rich`), and it shows the values
# of a standard set of features.

w = F.otype.s("word")[1]
F.atf.v(w)

A.pretty(w)

A.pretty(w, fmt="layout-orig-unicode", withNodes=True)

# By default, pretty displays descend to the word level, but you can also descend to the sign level:

A.pretty(w, baseTypes="sign")

A.pretty(w, fmt="layout-orig-unicode", baseTypes="sign", withNodes=True)

# Later on, in the [search](search.ipynb) tutorial we see that `pretty()` can also display other features,
# even features that you or other people have created and added later.
#
# Here we call for the feature `atf`, which shows the original atf for the sign in question
# excluding the bracketing characters.
#
# Consult the
# [feature documentation](https://github.com/Nino-cunei/oldbabylonian/blob/master/docs//transcription.md)
# to see what information is stored in all the features.
#
# We show it with node numbers, but you could leave them out in an obvious way.

A.pretty(f, extraFeatures="atf", fmt="layout-orig-rich", withNodes=True)

# We do not see much, because the default condense type is `line`, and a `document` is bigger than that.
# Objects bigger than de condense type will be abbreviated to a label that indicates their identity,
# not their contents.
#
# But we can override this by adding `full=True`.
#
# See also the documentation on [`pretty`](https://annotation.github.io/text-fabric/tf/advanced/display.html#tf.advanced.display.pretty).

A.pretty(f, extraFeatures="atf", fmt="layout-orig-rich", withNodes=True, full=True)

# # Layout formats: the details
#
# We give detailed examples of how the material is styled in the `layout-` formats.
#
# We show the representation of all kinds of signs and also what the influence of
# clustering and flags are.
#
# Here are the design principles:
#
# * all flags `# ? ! *` cause the preceding sign to be in bold
# * damage `#` and missing `[ ]` text is blurry and in grey
# * questioned `?` and uncertain `( )` text is in italics
# * remarkable `!` and supplied `< >` text is overlined, supplied text is in blue
# * excised `<< >>` text has a strike-through and is in red
# * collated `*` text is underlined
#
# **Numerals** are written with repeats/fractions and the repeated material is in `⌈ ⌉`.
# If represented in cuneiform unicode, repeated material is actually repeated that many times, and the repeat number and
# the brackets are not shown.
#
# **Ligatures** (the `x` operator as in `kux(DU)`) are written with the `␣` character between the operands, and the second
# operand (`DU`) is written between `⌈ ⌉`.
#
# **Corrections** (as in `ku!(LU)`) are written as `ku=⌈LU⌉`.
#
# Just a quick overview of the sign types:

F.type.freqList("sign")

# # Styled display of ATF text

lines = (
    (("P510536", "obverse", "15"), ("cluster: language", [1, 2, 3])),
    (("P509373", "obverse", "1"), ("cluster: determinative", [3])),
    (("P509375", "obverse", "3"), ("cluster: missing", [1, 2, 3, 6])),
    (("P510736", "reverse", "5"), ("cluster: uncertain", [6, 7, 8])),
    (("P510526", "obverse", "8"), ("cluster: supplied", [7, 8, 9])),
    (("P373056", "obverse", "11"), ("cluster: excised", [9, 10])),
    (("P510536", "obverse", "8"), ("flag: damage", [1, 2, 3, 6, 9, 10])),
    (("P297171", "reverse", "1"), ("flag: question", [3, 4, 5])),
    (("P510536", "obverse", "15"), ("flag: remarkable", [6])),
    (("P387299", "obverse", "5"), ("flag: collated", [1])),
    (("P510534", "reverse", "20'"), ("flag: damage + question", [3])),
    (("P497780", "reverse", "4"), ("flag: damage + remarkable", [1])),
    (("P305744", "obverse", "10"), ("flag: damage + collated", [5])),
    (("P305799", "left side", "1"), ("flag: collated + remarkable", [3, 5])),
    (("P305806", "reverse", "1"), ("flag: remarkable + question + collated", [3])),
    (("P305744", "obverse", "10"), ("flag collated in cluster missing", [6, 7])),
    (("P275088", "reverse", "2"), ("sign: comment", [1])),
    (("P510636", "obverse", "3"), ("sign: grapheme", [9])),
    (("P386451", "reverse", "11"), ("sign: correction", [6])),
    (("P312032", "left edge", "1"), ("sign: numeral", [4, 6])),
    (("P492284", "obverse", "5"), ("sign: ligature", [2, 3])),
    (("P509373", "reverse", "18'"), ("sign: unknown and ellipsis", [7, 8])),
)

for (line, (desc, positions)) in lines:
    ln = T.nodeFromSection(line)
    A.dm("---\n# {}\n\nLocation: {} {}:{}".format(desc, *line))
    s = L.d(ln, otype="sign")[0]
    highlights = {s + p - 1 for p in positions}
    print(*A.getSource(ln), sep="\n")
    A.plain(ln, fmt="layout-orig-rich", highlights=highlights)
    A.plain(ln, fmt="layout-orig-unicode", highlights=highlights)
    A.pretty(
        ln,
        extraFeatures="atf",
        fmt="text-orig-rich",
        baseTypes="sign",
        highlights=highlights,
    )

# ---
#
# All chapters:
#
# * **[start](start.ipynb)** introduction to computing with your corpus
# * **display** become an expert in creating pretty displays of your text structures
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
