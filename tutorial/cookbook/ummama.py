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

# # Between `um-ma` and `-ma`
#
# What happens between `um-ma` and `ma` can help to identify proper nouns.
#
# More precisely: we are looking for single words, immediately following the sign sequence `um-ma`, and where
# the word itself ends in `-ma`.

# +
import collections

from tf.app import use

# -

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# The following query captures the intention of finding words after `um-ma` ending in `-ma`.
#
# See [basic relations](https://annotation.github.io/text-fabric/tf/about/searchusage.html#relational-operators)
# for the meaning of `<:` and `:=`.
# You find them under **slot comparison**.

query = """
line
   sign reading=um
   <: sign reading=ma
   <: word
     := sign reading=ma
"""
results = sorted(S.search(query))
print(f"{len(results)} results")

A.table(results, start=1000, end=1010, fmt="layout-orig-rich")

# +
introNouns = collections.Counter()

for (line, um, ma1, word, ma2) in results:
    strippedWord = L.d(word, otype="sign")[:-1]
    introNouns[T.text(strippedWord, fmt="text-orig-rich")] += 1

len(introNouns)
# -

for (proper, amount) in sorted(
    introNouns.items(),
    key=lambda x: (-x[1], x[0]),
)[0:100]:
    print(f"{proper:<30} {amount:>4} x")

# Same exercise, now based on cuneiform unicode:

# +
introNounsU = collections.Counter()

for (line, um, ma1, word, ma2) in results:
    strippedWord = L.d(word, otype="sign")[:-1]
    introNounsU[T.text(strippedWord, fmt="text-orig-unicode")] += 1

len(introNounsU)
# -

# Less words. Presumably, some words that are different in ascii-reading are equal in cuneiform unicode.

for (proper, amount) in sorted(
    introNounsU.items(),
    key=lambda x: (-x[1], x[0]),
)[0:10]:
    print(f"{proper:<30} {amount:>4} x")

# But these are the wrong shapes: we need the Santakku font.
#
# Instead of counting the word strings, we collect the word nodes:

# +
introNounsU = collections.defaultdict(set)

for (line, um, ma1, word, ma2) in results:
    introNounsU[F.symu.v(word)].add(word)

len(introNounsU)

# +
fmtr = "layout-orig-rich"
fmtu = "layout-orig-unicode"

html = []
html.append("<table>")

for (proper, words) in sorted(
    introNounsU.items(),
    key=lambda x: (-len(x[1]), x[0]),
)[0:10]:
    firstWord = sorted(words)[0]
    amount = len(words)
    html.append(
        f"""
<tr>
  <td>{A.plain(firstWord, fmt=fmtr, withPassage=False, _asString=True)}</td>
  <td>{A.plain(firstWord, fmt=fmtu, withPassage=False, _asString=True)}</td>
  <td>{amount:>4}</td>
</tr>
"""
    )

html.append("</table>")

A.dh("".join(html))
