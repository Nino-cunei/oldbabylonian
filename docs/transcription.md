<img src="images/ninologo.png" align="right" width="200"/>
<img src="images/tf.png" align="right" width="200"/>

Feature documentation
=====================

Here you find a description of the transcriptions of the Old Babylonian Letter corpus (AbB),
the Text-Fabric model in general, and the node types, features of the
AbB corpus in particular.

See also [about](about.md) [text-fabric](textfabric.md)

Conversion from ATF to TF
-------------------------

Below is a description of document transcriptions in
ATF (see below)
and an account how we transform them into
[Text-Fabric](https://annotation.github.io/text-fabric/) format by means of
[tfFromAtf.py](../programs/tfFromAtf.py).

There are various pages with documentation on ATF at the ORACC site, notably:

* [CDLI ATF Primer](http://oracc.museum.upenn.edu/doc/help/editinginatf/cdliatf/index.html)
* [Structure Tutorial](http://oracc.museum.upenn.edu/doc/help/editinginatf/primer/structuretutorial/index.html)
* [Inline Tutorial](http://oracc.museum.upenn.edu/doc/help/editinginatf/primer/inlinetutorial/index.html)

One of the observations during conversion of this corpus from ATF to TF is, that the match between patterns 
described in the docs and the patterns seen in the sources is often difficult to make, and not always
perfect.

The Text-Fabric model views the text as a series of atomic units, called
*slots*. In this corpus [*signs*](#sign) are the slots.

On top of that, more complex textual objects can be represented as *nodes*. In
this corpus we have node types for:
[*sign*](#sign),
[*word*](#word),
[*cluster*](#cluster),
[*line*](#line),
[*face*](#face),
[*document*](#document).

The type of every node is given by the feature
[**otype**](https://annotation.github.io/text-fabric/Api/Features/#node-features).
Every node is linked to a subset of slots by
[**oslots**](https://annotation.github.io/text-fabric/Api/Features/#edge-features).

Nodes can be annotated with features. See the table below.

Text-Fabric supports up to three customizable section levels.
In this corpus we use only two:
[*document*](#document) and [*face*](#face).

Other docs
----------

[Text-Fabric API](https://annotation.github.io/text-fabric)

[Oldbabylonian API](https://annotation.github.io/app-oldbabylonian/blob/master/api.md)

[Utils API](utils.md)

Reference table of features
===========================

*(Keep this under your pillow)*

Node type [*sign*](#sign)
-------------------------

Basic unit containing a single `reading` and/or `grapheme` and zero or more *flags*.

There are several types of sign, stored in the feature `type`.

type | examples | description
------- | ------ | ------
`reading` | `ma` `qa2` | normal sign with a reading (lowercase)
`unknown` | `x` | representation of an unknown sign
`numeral` | `5(disz)` `5/6(disz)`  | a numeral, either with a repeat or with a fraction
`ellipsis` | `...` | representation of an unknown number of missing signs
`grapheme` | `ARAD2` `GAN2` | sign given as a grapheme (uppercase)
`empty` | `$ blank space` `# reading la-mi! proposed by Von Soden` | empty sign to fill a comment or meta line
`complex` | `szu!(LI)` `isx(USZ)` | complex sign with reading, operator and given grapheme
`comment` | `($ blank space $)` | comment sign to represent an *inline* comment

feature | values | in ATF | description
------- | ------ | ------ | -----------
**after** | `-` ` ` `:` `.` `/` `+` | `ha:a-am` `a-di ma-di` | what comes after a sign before the next sign
**atf** | `qa2` `ARAD2` `5/6(disz)` `ba?!(GESZ)` | idem | full atf of a sign, also complex signs, with flags but without clustering characters
**atfpost** | `}_` | `{ki}_` | clustering characters attached at the end of a sign
**atfpre** | `{` | `{ki}_` | clustering characters attached at the start of a sign
**collated** | `1` | `_8(gesz2)*` | indicates the presence of the *collated* flag `*`
**comment** | `blank space` | `($ blank space $)` | value of an inline comment; for such a comment a sign of type `comment` has been constructed; the `atf` feature of such a sign contains the full comment, including the delimiters `($` and `$)`
**damage** | `1` | `isz-ta#-a-lu` | indicates the presence of the *damage* flag `#`
**det** | `1` | `{d}suen` `asza5{a-sza3}` | indicates whether the sign is a determinative gloss, marked by being within braces `{ }`
**excised** | `1` | `<<ma>>` `<<ip-pa-ar-ra-as>>` | whether a sign is excised by the editor, marked by being within double angle brackets  `<< >>`
**fraction** | `5/6` | `5/6(disz)` | the fraction part of a numeral
**givengrapheme** | `LI` `USZ` | `szu!(LI)` `isx(USZ)` | the grapheme supplied between brackets after a reading in a complex sign
**grapheme** | `ARAD2` `GAN2` | idem | the grapheme name of a [*sign*](#sign) when its atf is capitalized
**langalt** | `1` | `_{d}suen_` | whether the sign is in the alternate language in this corpus *Sumerian*. See also the document feature `lang`. ATF marks alternate language by enclosing signs in `_` ... `_`
**missing** | `1` | `[ki-im]` | whether a sign is missing, marked by being within square brackets  `[ ]`
**operator** | `!` `x` | `szu!(LI)` `isx(USZ)` | the type of operator in a complex sign
**question** | `1` | `DU6~b?` | indicates the presence of the *question* flag `?`
**reading** | `suen` | idem | reading (lowercase) of a sign; the sign may be simple or complex
**remarkable** | `1` | `lam!` | indicates the presence of the *remarkable* flag `!`
**repeat** | `5` | `5(disz) ` | marks repetition of a grapheme in a numeric sign 
**supplied** | `1` | `<pa>` `i-ba-<asz-szi>` | whether a sign is supplied by the editor, marked by being within angle brackets  `< >`
**type** | | | type of sign, see table above
**uafter** | ` ` `:` `.` `/` `+` | | what comes after a sign before the next sign when represented with unicode characters
**uncertain** | `1` | `[x (x)]` `[li-(il)-li]` | whether a sign is uncertain, marked by being within brackets  `( )`
**unicode** | | | reading or grapheme of a sign represented as unicode characters

Node type [*word*](#word)
-------------------------
Sequence of signs separated by `-`. Sometimes the `-` is omitted. Very rarely there is an other character between two signs, such as `:` or `/`. Words themselves are separated by spaces.

feature | values | in ATF | description
------- | ------ | ------ | -----------
**atf** | `{disz}sze-ep-_{d}suen` | idem | full atf of a word, including flags and clustering characters

Node type [*cluster*](#cluster)
-------------------------------

Grouped sequence of [*signs*](#sign). There are different
types of these bracketings. Clusters may be nested.
But clusters of different types need not be nested properly with respect to each other.

The type of a cluster is stored in the feature `type`.

type | examples | description
------- | ------ | ------
`langalt` | `_  _` | alternate language
`det` | `{ }` | gloss, determinative
`uncertain` | `( )` | uncertain
`missing` | `[ ]` | missing
`supplied` | `< >` | supplied by the editor in order to get a reading
`excised` | `<< >>` | excised by the editor in order to get a reading

Each cluster induces a sign feature with the same name as the type of the cluster,
which gets value 1 precisely when the sign is in that cluster.

Node type [*line*](#line)
-------------------------

Subdivision of a containing [*face*](#face).

feature | values | in ATF | description
------- | ------ | ------ | -----------
**col** | `1` | `@column 1` | number of the column in which the line occurs; without prime, see also `primecol`
**comment** | `rest broken` | `$ rest broken` | the contents of a structural comment (starting with `$`); such a line has a single empty slot
**ln** | `1` `$` `#` | `1. [a-na]` `$ rest broken` `# reading la-mi! proposed by Von Soden` | ATF line number of a transcription line; for comment lines it is `$`, for meta lines it is `#`; without prime, see also `primeln`
**primecol** | `1'` | whether the column number has a prime `'` | 
**primeln** | `1'` | whether the line number has a prime `'` | 
**remarks** | `reading la-mi! proposed by Von Soden` | `# reading la-mi! proposed by Von Soden` | the contents of a remark targetedto the ocntents of a transcription line; the `remark` feature is present on the line that is being commented; multiple remark lines will be joined with a newline
**srcLn** |  |  | the literal text in the transcription at the start of the object; see [source data](#source-data)
**srcLnNum** |  |  | the line number of the transcription line at the start of the object; see [source data](#source-data)
**trans** | `1` | | indicates whether a line has a translation (in the form of a following meta line (`#`))
**translation@en** | `was given (lit. sealed) to me—` | `#tr.en: was given (lit. sealed) to me—` | English translation in the form of a meta line (`#`)

Node type [*face*](#face)
-------------------------

One of the sides of a [*document*](#document).

feature | values | in ATF | description
------- | ------ | ------ | -----------
**face** | `obverse` `reverse` `seal 1` `envelope - seal 1` | `@obverse` `@reverse` `@seal 1` | type of face, if on an object different from a tablet, the type of object is prepended
**object** | `tablet` `envelope` | `@tablet` `@envelope` | object on which a face is situated; seals are not objects but faces
**srcLn** |  |  | the literal text in the transcription at the start of the object; see [source data](#source-data)
**srcLnNum** |  |  | the line number of the transcription line at the start of the object; see [source data](#source-data)

Node type [*document*](#document)
-----------------------------

The main entity of which the corpus is composed, representing the transcription
of a complete clay document.

feature | values | in ATF | description
------- | ------ | ------ | -----------
**collection** | `AbB` | `&P509373 = AbB 01, 059` | the collection of a [*document*](#document)
**docnote** | `Bu 1888-05-12, 200` | `&P365091 = CT 02, pl. 10, Bu 1888-05-12, 200` | additional remarks in the document identification
**docnumber** | `059` | `&P509373 = AbB 01, 059` | the identification of a [*document*](#document) as number within a collection - volume
**lang** | `akk` `sux` |  | the language the document is written in. `akk` = *Akkadian*, `sux` = *Sumerian*. See the sign feature `langalt` for the language of smaller portions of the document
**pnumber** | `P509373` | `&P509373 = AbB 01, 059` | the P-number identification of a [*document*](#document)
**srcfile** |  |  | the source file name of the document, see [source data](#source-data)
**srcLn** |  |  | the literal text in the transcription at the start of the object; see [source data](#source-data)
**srcLnNum** |  |  | the line number of the transcription line at the start of the object; see [source data](#source-data)
**volume** | `01` | `&P509373 = AbB 01, 059` | the volume of a [*document*](#document) as number within a collection

Source data
===========

All nodes that correspond directly to a line in the corpus, also get features by
which you can retrieve the original transcription:

*   **srcfile** the name of the source file, is either `AbB-primary` or `AbB-secondary`;
*   **srcLn** the literal contents of the line in the source;
*   **srcLnNum** the line number of the corresponding line in the source file.

Slots
=====

We discuss the node types we are going to construct. A node type corresponds to
a textual object. Some node types will be marked as a section level.

Sign
----

This is the basic unit of writing.

**The node type [*sign*](#sign) is our slot type in Text-Fabric.**

### Signs in general ###

The defining trait of a sign is its *reading* and/or optinally its *grapheme*.

We will collect the name string of a sign, without variants and flags, and store
it in the sign feature **reading** if it is lowercase, and **grapheme** if it is uppercase.

Signs may be *augmented* with

*   flags

### Repeats and fractions ###

Signs, especially those with a numeric meaning, may be repeated.

    5(disz)

Numeric signs may also be preceded with a *fraction*:

    5/6(disz)

We store the integral number before the brackets in a feature called **repeat**,
and the fraction in the feature called *fraction*.

If the repeat is `n`, it means that a number is missing.

In a numeral, within the brackets you find the *reading* or *grapheme*.

After the closing bracket the numeral may be augmented with *flags*.

# AFTER THIS POINT MORE REWORKING HAS TO BE DONE

### Ordinary signs ###

An example of an ordinary sign is

    GAN2

### Missing signs ###

This notation denotes missing signs.

    [...]

In the syntax of transcriptions, this is a one-element [*cluster*](#cluster),
bracketed with `[ ]`, with a special sign in it `...`, meaning: one or more
missing graphemes.

We treat the `...` sign as a single sign `…`, and we treat the cluster as any
other cluster.

### Type ###

Not everything we see in the transcription as graphemes is a proper grapheme.
That is why we also have a feature **type** that makes it easy to detect what is
the case.

TF | ATF | type | explanation
--- | --- | ---- | -----------
`` \| *not present* \| `empty` \| these are signs inserted by the conversion where it was needed to fit the model of Text-Fabric |  |  | 
`…` | `...` | `ellipsis` | one or more missing signs
`X` | `X` | `unknown` | an unknown sign
`N01` | `N01` | `numeral` | a numeral, usually as a repeat: `7(N01)`. A single `N` is also treated as a numeral.
`GISZ` | `GISZ` | `ideograph` | an ordinary grapheme

#### Flags ####

Outer [*quads*](#quad) and *signs* may have *flags*. Sub-*quads* do not have
them. In transcription they show up as a special trailing character. Flags code
for things like damage, uncertainty, and correction.

##### Collation #####

Flag `*`.

Collected as **collated** = `1`

Not encountered yet.

##### Damage #####

Flag `#`.

Collected as **damage** = `1`

Example:

    1.  1(N48) 7(N34) 3(N14) , BARA2~a#

##### Question #####

Flag `?` Unsure identification.

Collected as **question** = `1`.

Example:

    1.  1(N45) 8(N14)# , X SZE~a MA2?

##### Correction #####

Flag `!` or `!(` *written* `)`

A bare `!` is collected as **remarkable** = `1`

The full form indicates that the sign has been corrected (like in Hebrew
*ketiv/qere*).

The sign between the brackets is what is written (ketiv), the sign before the
`!` is the corrected form (qere).

Collected as **written** = *written*. In this case, we do not set the
**remarkable** feature to `1`.

Example:

    5.  1(N01) , NAM2 URU~a1!(GURUSZ~a)?

Note that flags on a numeral are written within the brackets.

There may be multiple flags:

    1.  1(N48) 7(N34) 3(N14) , BARA2~a#

The other nodes
===============

Cluster
-------

One or more [*quads*](#quad) may be bracketed by `( )` or by `[ ]` or by `< >`:
together they form a *cluster*.

    2.c. , (|GIR3~cxSZE3|# NUN~a# [...])a

    3.  [...] , [MU |ZATU714xHI@g~a|]

    4.b1. <7(N14) , GAN2>

Note that a cluster may contain just one [*quad*](#quad).

### Missing signs ###

Clusters with `[ ]` indicate that there are missing signs here.

Collected in a feature **type** = `[`

### Supplied signs ###

Clusters with `< >` indicate that these signs have been supplied in order to
make sense.

Collected in the feature **type** = `supplied`

Comments
--------

Lines starting with `$` or `#` are *comments* to the current object
([*document*](#document), [*face*](#face), [*column*](#column), or [*line*](#line).

Lines starting with `@object` are comments to the current object.

    &P002718 = ATU 3, pl. 078, W 17729,cn+
    #version: 0.1
    #atf: lang qpc

and

    4.  1(N01) , [...]
    $ rest broken
    @column 3
    $ beginning broken

Comments are a separate node type. They get one slot with an empty grapheme to
anchor them to the text.

The type of comment is stored in the feature **type**:

transcription | **type** feature | description
------------- | ---------------- | -----------
`$` | `ruling` | a rule like marking on the document
`#` | `meta` | metadata
`@object` | `object` | object description

The line number and the text on the line are collected in features **srcLnNum**
and **srcLn** respectively.

There is also an edge feature **comments**, with edges going from the object to
its *comments* nodes.

By using

    E.comments.f(t)

we get the list of *comments* nodes to document node `t` in a straigthforward way;
this list does not contain the *comments* to the *faces*, *columns*, *lines* of
the *document*.

Likewise, by using

    E.comments.t(c)

we get the object to which *comment* `c` is targeted.

Line
----

A node of type *line* corresponds to an undivided line or to all
[*cases*](#case) whose numbers start with the same decimal number.

**This node type is section level 3.**

If we encounter a line without a preceding [*column*](#column) specifier we
proceed as if we have seen a `@column 0`.

The **number** of a line is always a single number, without a hierarchical
structure.

If a line is terminal, i.e. undivided, we give it a feature **terminal** with
value `1`, otherwise we do not assign the feature **terminal**.


Column
------

[*Lines*](#line) are grouped into *columns*.

*Columns* are marked by lines like

    @column number

A node of type *column* corresponds to the material after the *column* specifier
and before the next next *column* specifier or the end of a [*face*](#face) or
[*document*](#document).

**This node type is section level 2.**

The number of a column is stored in the feature **number**. However, this number
is not suitable as a section number, because a *document* may have multiple faces
(which we do not take as a section level), and each of the faces restart the
*column* numbering.

We add a feature **fullNumber** to columns, filled with the type of the face
(see below) and the column **number**, separated by a `:`.

There might be a prime `'` after the number, but before the last `.` If present,
it indicates that the number does not count objects on the document in its
original state, but in its present state. If the document is damaged, material is
missing, and the missing items are not numbered.

In the presence of a prime, we add a feature **prime** with value `1` and we
remove the prime from the *column* number.

Face
----

[*Columns*](#column) are grouped into [*faces*](#face).

*Faces* are marked by lines like

    @obverse

or

    @reverse

There are a few other possibilities:

    @bottom
    @left
    @top
    @surface identifier
    @seal identifier

A node of type *face* corresponds to the material after a *face* specifier and
before the next *face* specifier or the end of a [*document*](#document).

**This node type is not a section level!**

We make a feature **type** for this node type, which contains the name of the
*face*, e.g. `obverse`, `reverse`.

We also make a feature **identifier**, which contains the identifier if the
**type** is `surface` or `seal`.

`@seal` is never followed by linguistic content.

If there are columns outside a *face*, we act as if we have seen a `@noface`,
i.e. we insert a *face* with the name `noface`.

Document
------

[*Faces*](#face) are grouped into *documents*.

*Tablets* are marked by lines like

    @document

Sometimes this line sometimes missing. The surest sign of the beginning of a
*document* is a line like

    &P002174 = ATU 6, pl. 48, W 14731,?4

Here we collect `P002174` as the **pnumber** of the *document*, and
`ATU 6, pl. 48, W 14731,?4` as the document **name**.

We also add the name of the corpus as a feature **period**.

A node of type *document* corresponds to the material after a *document* specifier
and before the next *document* specifier.

**This node type is section level 1.**

Our corpora are just sets of *documents*. The position of a particular document in
the whole set is not meaningful. The main identification of documents is by their
**pnumber** (in this case *P number*), not by any sequence number within the
corpus.

We also added the feature **excavation**, containing the excavation number(s) of
the document. These numbers are given in the full source files as metadata; they
are not in the pure transcription files on which the rest of the conversion is
based.

Subsequent lines starting with `#` or `@object` are treated as
[*comments*](#comment).

Empty objects
=============

If objects such as [*tablets*](#document), [*faces*](#face), [*columns*](#column),
[*lines*](#line), and [*comments*](#comment) lack textual material, they will
not have slots. This is incompatible with the Text-Fabric model, where all nodes
must be anchored to the slots. We will take care that if textual material is
missing, we insert a special [*sign*](#sign). This is a sign with **grapheme** =
`''`, the empty string.

Not that quite a few of the empty [*signs*](#sign) we thus create, are for
[*comments*](#comment). These are the only [*signs*](#sign) that do not occur
within [*quads*](#quad).

Warning
=======

In order to produce transcribed text you cannot rely on features of slots alone.
Every node type introduces bits of syntax in the transcription.
