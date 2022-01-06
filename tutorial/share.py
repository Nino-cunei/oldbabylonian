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
# # Sharing data features
#
# ## Explore additional data
#
# Once you analyse a corpus, it is likely that you produce data that others can reuse.
# Maybe you have defined a set of proper name occurrences, or special numerals, or you have computed part-of-speech assignments.
#
# It is possible to turn these insights into *new features*, i.e. new `.tf` files with values assigned to specific nodes.
#
# ## Make your own data
#
# New data is a product of your own methods and computations in the first place.
# But how do you turn that data into new TF features?
# It turns out that the last step is not that difficult.
#
# If you can shape your data as a mapping (dictionary) from node numbers (integers) to values
# (strings or integers), then TF can turn that data into a feature file for you with one command.
#
# ## Share your new data
# You can then easily share your new features on GitHub, so that your colleagues everywhere
# can try it out for themselves.
#
# You can add such data on the fly, by passing a `mod={org}/{repo}/{path}` parameter,
# or a bunch of them separated by commas.
#
# If the data is there, it will be auto-downloaded and stored on your machine.
#
# Let's do it.

# %load_ext autoreload
# %autoreload 2

# +
import collections
import os

from tf.app import use

# -

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())
# A = use('oldbabylonian', hoist=globals())

# # Making data
#
# We illustrate the data creation part by creating a new feature, `ummama`.
# The idea is that we mark every sign reading that occurs between `um-ma` and `ma` some where in the first 3 lines of a face.
# We want to mark every occurrence of such signs elsewhere in the corpus with `ummama=1`.
#
# We only do it if the sign between the `um-ma` and `ma` (which must be on the same line) is not missing, damaged, or questionable.
#
# The easiest way to get started is to run a query:

query = """
line ln<4
  =: sign reading=um missing# damage# question#
  <: sign reading=ma missing# damage# question#
% the next sign is the one that we are after
  < sign missing# damage# question#
  < sign reading=ma missing# damage# question#
"""

results = A.search(query)

A.table(results, end=10)

# Observe how the signs between `um-ma` and `ma` are picked up, except the damaged `nu` and `ur2`.
#
# First we are collect these readings, and survey the frequencies in the result.
#
# Some signs do not have a reading, but then they have a grapheme.
# If they do not have a grapheme, they might be comment signs, and we skip them.

# +
umaReadings = collections.Counter()

# collect

for (line, um, ma1, sign, ma2) in results:
    reading = F.reading.v(sign) or F.grapheme.v(sign)
    if not reading:
        continue
    umaReadings[reading] += 1

# show

print(f"Found {len(umaReadings)} distinct readings")
limit = 20

for (reading, amount) in sorted(
    umaReadings.items(),
    key=lambda x: (-x[1], x[0]),
)[0:limit]:
    print(f"{reading:<6} {amount:>4} x")
print(f" ... and {len(umaReadings) - limit} more ...")
# -

# Now we visit all signs in the whole corpus and check whether their reading or grapheme is in this set.
# If so, we give that sign a value 1 in the dictionary `ummama`.

# +
ummama = {}

allSigns = F.otype.s("sign")

for s in allSigns:
    reading = F.reading.v(s) or F.grapheme.v(s)
    if not reading:
        continue
    if reading in umaReadings:
        ummama[s] = 1

print(f"Assigned `ummama=1` to {len(ummama)} sign occurrences out of {len(allSigns)}")
# -

# Note that the majority of all signs also occurs between `um-ma` and `ma` at the start of a document.
#
# Maybe this is an indication that we are not capturing the idea of selecting specific signs,
# we may have to strengthen our search criterion.
#
# But that is beyond this tutorial. We suppose these ummama words form a valueable set that we want to share.

# # Saving data
#
# The [documentation](https://annotation.github.io/text-fabric/tf/core/fabric.html#tf.core.fabric.FabricCore.save)
# explains how to save this data into a text-fabric
# data file.
#
# We choose a location where to save it, the `exercises` repository in the `Nino-cunei` organization, in the folder `analysis`.
#
# In order to do this, we restart the TF api, but now with the desired output location in the `locations` parameter.

GITHUB = os.path.expanduser("~/github")
ORG = "Nino-cunei"
REPO = "exercises"
PATH = "bab-analysis"
VERSION = A.version

# Note the version: we have built the version against a specific version of the data:

A.version

# Later on, we pass this version on, so that users of our data will get the shared data in exactly the same version as their core data.

# We have to specify a bit of metadata for this feature:

metaData = {
    "ummama": dict(
        valueType="int",
        description="reading occurs somewhere between um-ma and ma",
        creator="Dirk Roorda",
    ),
}

# Now we can give the save command:

TF.save(
    nodeFeatures=dict(ummama=ummama),
    metaData=metaData,
    location=f"{GITHUB}/{ORG}/{REPO}/{PATH}/tf",
    module=VERSION,
)

# # Sharing data
#
# How to share your own data is explained in the
# [documentation](https://annotation.github.io/text-fabric/tf/about/datasharing.html).
#
# Here we show it step by step for the `ummama` feature.
#
# If you commit your changes to the exercises repo, and have done a `git push origin master`,
# you already have shared your data!
#
# If you want to make a stable release, so that you can keep developing, while your users fall back
# on the stable data, you can make a new release.
#
# Go to the GitHub website for that, go to your repo, and click *Releases* and follow the nudges.
#
# If you want to make it even smoother for your users, you can zip the data and attach it as a binary to the release just created.
#
# We need to zip the data in exactly the right directory structure. Text-Fabric can do that for us:

# + language="sh"
#
# text-fabric-zip Nino-cunei/exercises/bab-analysis/tf
# -

# All versions have been zipped, but it works OK if you only attach the newest version to the newest release.
#
# If a user asks for an older version in this release, the system can still find it.

# Here is the result for our case
#
# ![ummama](images/ummama.png)

# # Use the data
#
# We can use the data by calling it up when we say `use('oldbabylonian', ...)`.
#
# Here is how:

A = use(
    "oldbabylonian:clone",
    checkout="clone",
    hoist=globals(),
    mod="Nino-cunei/exercises/bab-analysis/tf:clone",
)
# A = use('oldbabylonian', hoist=globals(), mod='Nino-cunei/exercises/bab-analysis/tf')

# Above you see a new section in the feature list: **Nino-cunei/exercises/analysis/tf** with our foreign feature in it: `ummama`.
#
# Now, suppose did not know much about this feature, then we would like to do a few basic checks:

F.ummama.freqList()

# We see that the feature has only one value, `1`, and that 182222 nodes have it.

# Which nodes have a ummmama feature?

{F.otype.v(n) for n in N.walk() if F.ummama.v(n)}

# Only signs have the feature.
#
# Let's have a look at a table of some ummama signs.

results = A.search(
    """
sign ummama
"""
)

A.table(results, start=1, end=20)

# Now let's get some non-ummama signs:

results = A.search(
    """
sign ummama#
"""
)

A.table(results, start=1, end=20)

# Let's get lines with both ummama and non-ummama signs:

results = A.search(
    """
line
  sign ummama
  sign ummama#
"""
)

A.table(results, start=1, end=2, condensed=True)

# With highlights:

# +
highlights = {}

for s in F.otype.s("sign"):
    color = "lightsalmon" if F.ummama.v(s) else "mediumaquamarine"
    highlights[s] = color
# -

A.table(
    results, start=1, end=10, baseTypes="sign", condensed=True, highlights=highlights
)

# If we do a pretty display, the `ummama` feature shows up.

A.show(
    results,
    start=1,
    end=3,
    baseTypes="sign",
    condensed=True,
    withNodes=True,
    highlights=highlights,
)

# Or in the context of a whole face:

A.show(
    results,
    start=1,
    end=1,
    condensed=True,
    condenseType="face",
    withNodes=False,
    highlights=highlights,
)

# # All together!
#
# If more researchers have shared data modules, you can draw them all in.
#
# Then you can design queries that use features from all these different sources.
#
# In that way, you build your own research on top of the work of others.

# Hover over the features to see where they come from, and you'll see they come from your local github repo.

# ---
#
# All chapters:
#
# * **[start](start.ipynb)** become an expert in creating pretty displays of your text structures
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **[search](search.ipynb)** turbo charge your hand-coding with search templates
# * **[exportExcel](exportExcel.ipynb)** make tailor-made spreadsheets out of your results
# * **share** draw in other people's data and let them use yours
# * **[similarLines](similarLines.ipynb)** spot the similarities between lines
#
# ---
#
# See the [cookbook](cookbook) for recipes for small, concrete tasks.
#
# CC-BY Dirk Roorda
