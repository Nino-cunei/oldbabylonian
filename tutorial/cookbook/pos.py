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
# To see the pos tag creation: consult [posTag](posTag.ipynb)
#
# ---
#
# # Use the Part of Speech tagging

# # Usage
#
# For now, you can make use of a bunch of sets in your queries, whether in the TF-browser or in a notebook.
#
# ## Getting the sets
#
# Here is how you can get the sets.
#
# ### With Dropbox
#
# If you are synchronized to the `obb` shared folder on Dropbox
# (that means, you have installed the Dropbox client and accepted the invitation to `obb`):
#
# You are all set, you have the newest version of the sets file on your computer seconds after
# it has been updated.
#
# ### With Github
#
# First get the tutorials repo:
#
# For the first time:
#
# ```sh
# # cd ~/github/annotation
# git clone https://github.com/annotation/tutorials
# ```
#
# Advice: do not work in your clone directly, but in a working directory outside this clone.
# When you want to get updates the repo:
#
# ```sh
# # cd ~/github/annotation/tutorials
# git pull origin master
# ```
#
# (This will fail if you have worked inside your clone).
#
# ## Using the sets and features
#
# You can use the sets and features directly in your programs, or in TF-queries, whether in notebooks or in the TF-browser.
#
# ### TF-browser
#
# To start the TF browser:
#
# ```sh
# text-fabric oldbabylonian --sets=~/Dropbox/obb/sets.tfx --mod=annotation/tutorials/oldbabylonian/cookbook/pos/tf
# ```
#
# or
#
# ```sh
# text-fabric oldbabylonian --sets=~/github/annotation/tutorials/oldbabylonian/cookbook/sets.tfx --mod=annotation/tutorials/oldbabylonian/cookbook/pos/tf
# ```
#
# ### In notebooks
#
# This notebook is an example of how you can work with the new data.
#
# ## Using sets in queries
#
# You can use the names of sets in all places where you currently use `word`, `sign`, `face`, etc.
# More info in the [docs](https://annotation.github.io/text-fabric/tf/about/searchusage.html).

from tf.app import use
from tf.lib import readSets

A = use(
    "oldbabylonian:clone",
    version="1.0.4",
    checkout="clone",
    hoist=globals(),
    mod="annotation/tutorials/oldbabylonian/cookbook/pos/tf:clone",
)
# A = use('oldbabylonian', hoist=globals(), mod='annotation/tutorials/oldbabylonian/cookbook/pos/tf')

# Note that the features `pos` and `subpos` and friends are loaded now.
#
# Let's print the frequency lists of their values.
# First a convenience function to print the frequency list of an arbitrary feature.


def freqList(feat):
    for (p, n) in Fs(feat).freqList():
        print(f"{p:<12}: {n:>5} x")


freqList("pos")

freqList("subpos")

freqList("cs")

freqList("ps")

freqList("gn")

freqList("nu")

# We still need to load the sets.

sets = readSets("~/github/annotation/tutorials/oldbabylonian/cookbook/sets.tfx")
sorted(sets)

# We perform a query with the new sets:

query = """
pclneg
<: noun
"""
results = A.search(query)

# Oops! We need to tell `A.search()` to use the sets.

query = """
pclneg
<: noun
"""
results = A.search(query, sets=sets)

A.table(results, end=10)

# Why not ask for preposition-pronoun combinations?

query = """
pclneg
<: prnprs
"""
results = A.search(query, sets=sets)

A.table(results, end=10)
