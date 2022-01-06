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

# For the main tutorial go to [start](../start.ipynb)
#
# ---

# # Prepositions
#
# Prepositions play a role in finding nouns.
#
# Here we do some basic exploration.

from tf.app import use


A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# This is a list of prepositions:
#
# ```
# i-na
# a-na
# e-li
# isz-tu
# it-ti
# ```
#
# # Exploratory excursions
#
# Before we formulate a query to draw out the prepositions and their subsequent words,
# let's do some exploration.
# We'll need queries that are a bit more advanced as well, and we'll take a moment to explain
# what is going on.
#
# The first question is: do prepositions stand on their own as words, or are they part of words?
# Can they cross word boundaries?
#
# Let's check this out for the first preposition `i-na`:
#
# ## i-na as complete word
#
# First we look for all complete words that are made up of two signs, with readings `i` and `na` respectively.

queryW = """
word
  =: sign reading=i
  <: sign reading=na
  :=
"""

# Remember:
#
# * indentation in the template above means means that the indented objects
#   must be contained (embedded) in its less indented parent object:
#   the signs are embedded in the word;
# * `=:` connects the `words` with the first `sign`,
#   and the meaning is: both must *start* at the same slot;
# * `<:` connects the first sign with the second one,
#   and the meaning is that the first sign must immediately precede the second one;
# * `:=` connects the second sign with the word,
#   and the meaning is that both must *end* at the same slot.
#
# **Hint** Do you find it hard to remember what is what between `:=` and `=:`?
# Look at the position of the `=`:
#
# * in `:=` the `=` comes last, and the meaning is:
#   both *end* at the same slot.
# * in `=:` the `=` comes first, and the meaning is:
#   both *start* at the same slot.

resultsW = A.search(queryW)

A.table(resultsW, end=10)

# In order to provide a bit more context, we add lines to the query:

queryL = """
line
  word
    =: sign reading=i
    <: sign reading=na
    :=
"""

resultsL = A.search(queryL)

A.table(resultsL, condensed=False, end=10)

# Just in case you wonder whether a word can cross a line boundary, let us check that.

# +
suspect = []

for w in F.otype.s("word"):
    signs = L.d(w, otype="sign")
    firstSign = signs[0]
    lastSign = signs[-1]
    firstLine = L.u(firstSign, otype="line")[0]
    lastLine = L.u(lastSign, otype="line")[0]
    if firstLine != lastLine:
        suspect.append((w, firstLine, lastLine))

len(suspect)
# -

# Rest reassured: every word lies neatly in its own single line.

# ## `i` followed by `na` anywhere
#
# Now we look for adjacent pairs of signs of which the first has reading `i` and the second reading `na`.
# We do not care whether both signs are in the same word or even the same line, or face or document!

query = """
sign reading=i
<: sign reading=na
"""

results = A.search(query)

# Definitely more results. We want to show the extra cases.
#
# There are two possibilities:
#
# * the signs lie within a bigger word
# * the signs lie in two distinct words
#
# Let's query for them separately and see whether the numbers add up.

queryB = """
word
/with/
  sign
  <: sign
  <: sign
/-/
  sign reading=i
  <: sign reading=na
"""

# Explanation: in this query you see a new construct: a *quantifier*, namely `/with/` ... `/-/`.
#
# The *with* imposes a condition on the preceding atom: `word`.
# This particular condition states that the word must have at least three consecutive signs.
# These three signs will not be listed in the results.
#
# Words that satisfy this condition, will then be matched against the rest: that there are adjacent signs with `i` and `ma`.
#
# For more quantifiers, read the
# [docs](https://annotation.github.io/text-fabric/tf/about/searchusage.html#quantifiers)

resultsB = A.search(queryB)

A.table(resultsB, end=10)

# It seems that these words happen to start with `i-na`. Is that the case for all of these?
#
# Let's filter out the ones that do not start with `i`.

nonIstart = [(w, s1, s2) for (w, s1, s2) in resultsB if F.reading.v(s1) != "i"]
len(nonIstart)

# So, indeed, all these cases are words that start with `i-na`, so we can consider these as words with the preposition `i-na` prefixed.

# Well, 1440 + 325 = 1765, so we expect 3 cases where the `i` and `na` split a word.

queryS = """
w1:word
  s1:sign reading=i

w2:word
  s2:sign reading=na

w1 < w2
s1 <: s2
"""

# Explanation. Again something new: we can give *names* to the objects in our query and use those names
# to state relational constraints later on.
#
# So here we look for two words, one containing a sign `i` and the other containing a sign `na`.
#
# The extra conditions are that `w1` and `w2` are not equal (in fact, we state that `w1` comes before `w2`.
#
# And the two signs must be adjacent: `s1 <: s2`.

resultsS = A.search(queryS)

A.table(resultsS)

# For context, we query them in their lines:

queryS = """
line
  w1:word
    s1:sign reading=i

  w2:word
    s2:sign reading=na

w1 < w2
s1 <: s2
"""

resultsS = A.search(queryS)

A.table(resultsS)

# Finally, we come up with a query that looks for all `i-na` that are at the start of a word, including the cases where
# `i-na` is the whole word. In that case, we also want the next word included in our query.
#
# We cannot easily express this kind of if statement within our query, so we just ask for the words starting with `i-na`
# and we'll process the results to get the following word, if needed.
#
# If there is an `i-na` at the end of a line, we are not interested in it.

query = """
line
  word
    =: sign reading=i
    <: sign reading=na
"""

results = A.search(query)

A.table(results, end=10)

# # All prepositions
#
# Now let's query for all words that start with a preposition.

query = """
word
/with/
  =: sign reading=i
  <: sign reading=na
/or/
  =: sign reading=a
  <: sign reading=na
/or/
  =: sign reading=e
  <: sign reading=li
/or/
  =: sign reading=isz
  <: sign reading=tu
/or/
  =: sign reading=it
  <: sign reading=ti
/-/
"""

# Explanation: we have already encountered the `/with/` quantifiers. Now we see it in its full form: as a list of alternatives.
#
# Again: none of the sign nodes that attest the alternatives, end up in the results.
#
# That does not matter, we only want the words.
#
# With the list of words in hand, we are going to make a hand-coded tuple of all cases with nice highlighting.

rawResults = A.search(query)

rawResults[0:10]

# `rawResults` is a tuple of singleton tuples, each containing just a word node.
#
# In the following code, we walk through all the results, and
#
# * retrieve the containing line
# * highlight the preposition within the word
# * highlight the remaining material in the word in a different color
# * if there is no remaining material in the word, draw in the next word and highlight that.

# +
results = []
highlights = {}

for (w,) in rawResults:
    line = L.u(w, otype="line")[0]
    signs = L.d(w, otype="sign")
    highlights[signs[0]] = "orange"
    highlights[signs[1]] = "orange"
    if len(signs) > 2:
        noun = signs[2:]
    else:
        nextWord = L.n(w, otype="word")[0]
        noun = L.d(nextWord, otype="sign")
    for s in noun:
        highlights[s] = "aquamarine"
    results.append((line, w, nextWord))
# -

A.table(results, end=10, highlights=highlights)

A.table(results, start=1000, end=1010, highlights=highlights)

A.table(results, start=6000, end=6010, highlights=highlights)

# Finally, lets export this table to Excel.
#
# We use the function [`A.export()`](https://annotation.github.io/text-fabric/tf/advanced/display.html#tf.advanced.display.export).
#
# If we pass it our results and nothing else, it will write them to `results.tsv`, a file you
# can open in Excel.
#
# We will not see the highlights there, though.

A.export(results)

# But we also like it in rich text and in unicode:

A.export(results, toFile="resultsRich.tsv", fmt="text-orig-rich")
A.export(results, toFile="resultsUnicode.tsv", fmt="text-orig-unicode")

# Here are a few screenshots:
#
# ![resultsRich](images/prepExcelRich.png)
#
# In the next one we have manually set the font to Santakku in Excel for the relevant columns.
#
# ![resultsUnicode](images/prepExcelUnicode.png)

# Note that these Excel files have nearly 7000 rows.
#
# You can filter as you like.
#
# It is also easy to include more columns with refined information on the basis of which you can group and sort in additional ways.
