import sys
import os
import re
import collections
from shutil import rmtree
from glob import glob
from tf.fabric import Fabric
from tf.convert.tokens import Token

# LOCATIONS

BASE = os.path.expanduser('~/github')
ORG = 'Nino-cunei'
REPO = 'oldbabylonian'
VERSION = '0.1'
REPO_DIR = f'{BASE}/{ORG}/{REPO}'

TRANS_DIR = f'{REPO_DIR}/sources/cdli/transcriptions'

IN_DIR = f'{TRANS_DIR}/{VERSION}'

TF_DIR = f'{REPO_DIR}/tf'
OUT_DIR = f'{TF_DIR}/{VERSION}'


# ATF INTERPRETATION

clusterChars = {
    '_': '_',
    '<': '>',
    '[': ']',
}
clusterCharsInv = {ce: cb for (cb, ce) in clusterChars.items()}

markChars = {
    '+': 'plus',
    '*': 'star',
    '!': 'exclamation',
    '?': 'uncertain',
    '#': 'damage',
}

# TF CONFIGURATION

slotType = 'sign'

generic = {
    'name': 'AbB Old Babylonian Cuneiform',
    'editor': 'Cale Johnson et. al.',
    'institute': 'CDL',
    'converters': 'Cale Johnson, Dirk Roorda',
}

otext = {
    'fmt:text-orig-full': '{atf}{after}',
    'fmt:text-ling-full': '{reading}{after}',
    'fmt:text-graphic-full': '{grapheme}{after}',
    'sectionFeatures': 'pnumber,type',
    'sectionTypes': 'tablet,face'
}

intFeatures = set('''
    language
    super
'''.strip().split()) | set(markChars.values())

featureMeta = {
    'pnumber': {
        'description': 'catalog id of a tablet',
    },
    'srcfile': {
        'description': 'source file name of a tablet',
    },
    'srcln': {
        'description': 'line number in source file',
    },
    'srcline': {
        'description': 'full line in source file',
    },
    'ln': {
        'description': 'ATF line number',
    },
    'type': {
        'description': 'name of a face of a tablet or type of cluster',
    },
    'subtype': {
        'description': 'additional qualification of a face of a tablet',
    },
    'atf': {
        'description': 'full atf of a sign',
    },
    'reading': {
        'description': 'reading of a sign',
    },
    'grapheme': {
        'description': 'grapheme of a sign',
    },
    'after': {
        'description': 'what comes after a sign (- or space or nothing)',
    },
    'language': {
        'description': 'language of a sign: 1 = main, 2 = alternate',
    },
    'super': {
        'description': 'whether a sign is in superscript (between braces)',
    },
    'damage': {
        'description': 'whether a sign is damaged',
    },
    'uncertain': {
        'description': 'whether a sign is uncertain',
    },
    'exclamation': {
        'description': 'whether a sign has a lonely exclamation mark',
    },
    'star': {
        'description': 'whether a sign has a lonely star',
    },
    'plus': {
        'description': 'whether a sign has a lonely plus',
    },
    'givengrapheme': {
        'description': 'grapheme given in transcription by !()',
    },
}


# ATF PATTERNS

transRe = re.compile(r'''^([0-9a-zA-Z'.])+\s+(.*)$''')
numeralRe = re.compile(r'''[0-9]+\(([^)]+)\)''')
graphemeRe = re.compile(r'''!\(([^)]+)\)''')
splitRe = re.compile(r'''[ \t{}<>\[\].]+''')
stickyNumeralRe = re.compile(r'''([0-9]+\([^)]+\){2,})''')
numeral2Re = re.compile(r'''([0-9]+\([^)]+\))''')
stickyNumeralRe = re.compile(r'''((?:[0-9]+\([^)]+\)){2,})''')


def stickyNumeralRepl(match):
  return ' '.join(numeral2Re.findall(match.groups()[0]))


# ERROR HANDLING

def showErrors(errors, batch=10):
  if not errors:
    print('No errors')
  else:
    for (error, srcs) in sorted(errors.items()):
      print(f'ERROR {error}')
      for (src, data) in sorted(srcs.items()):
        print(f'\t{src} ({len(data)}x)')
        for (l, line, sore) in sorted(data)[0:batch]:
          soreRep = '' if sore is None else f'"{sore}" in '
          print(f'\t\t{l}: {soreRep}{line}')
        if len(data) > batch:
          print(f'\t\t + more')


# SET UP CONVERSION

def getSources():
  if os.path.exists(OUT_DIR):
    rmtree(OUT_DIR)
  os.makedirs(OUT_DIR, exist_ok=True)

# list all sources

  return tuple(
      os.path.splitext(os.path.basename(f))[0]
      for f in glob(f'{IN_DIR}/*.txt')
  )


def getTokenObj():
  TF = Fabric(locations=OUT_DIR)
  return Token(TF)


# TOKEN GENERATOR

def generateTokens(sources, token):

  curTablet = None
  curFace = None
  curLine = None
  curCluster = collections.defaultdict(list)
  pNum = None

  errors = collections.defaultdict(lambda: collections.defaultdict(set))

  # sub generators will be called by yield from expressions

  # sub gen: setting up a tablet node

  def tabletStart():
    nonlocal curTablet

    yield token.terminate(curTablet)
    curTablet = yield token.node('tablet')
    yield token.terminate(curFace)
    yield token.terminate(curLine)
    for cNodes in curCluster.values():
      for cNode in curCluster:
        yield token.terminate(cNode)
    curCluster.clear()

  # sub gen: adding data to a tablet node

  def tabletData():
    nonlocal pNum

    pNum = line[1:].split()[0]
    sys.stderr.write(f'{src:<15} : {i:>4} : {pNum:<20}\r')

    yield token.feature(
        curTablet,
        pnumber=pNum,
        srcfile=src,
        srcln=i,
        srcline=line,
    )

  # sub gen: terminating a tablet node

  def tabletEnd():
      yield token.terminate(curTablet)
      yield token.terminate(curFace)
      yield token.terminate(curLine)

  # sub gen: setting up a face node

  def faceStart():
    nonlocal curFace

    fields = line[1:].split(maxsplit=1)
    typ = fields[0]
    if typ == 'tablet':
      return

    yield from faceInsert(typ)

    if len(fields) == 2:
      yield token.feature(subtype=fields[1])

  # sub gen: inserting a default face node if no face is specified

  def faceInsert(typ):
    nonlocal curFace

    yield token.terminate(curFace)
    curFace = yield token.node('face')

    yield token.feature(
        type='obverse',
        srcfile=src,
        srcln=i,
        srcline=line,
    )

  # sub gen: setting up a line node

  def lineStart(ln, trans):
    nonlocal curLine

    yield token.terminate(curLine)
    curLine = yield token.node('line')

    yield token.feature(
        ln=ln,
        srcfile=src,
        srcln=i,
        srcline=line,
    )

    for (cb, ce) in clusterChars.items():
      if cb == ce:
        ncs = trans.count(cb)
        if ncs % 2:
          errors[f'unbalanced cluster of type "{cb}"'][src].add((i, line, None))
      else:
        if trans.count(cb) != trans.count(ce):
          errors[f'unbalanced cluster of type "{cb} {ce}"'][src].add((i, line, None))

    if stickyNumeralRe.findall(trans):
      trans = stickyNumeralRe.sub(stickyNumeralRepl, trans)

  # sub gen: adding data to a line node
  # this is itself a complicated generator with sub gens

  def lineData(trans):
    nonlocal curLine

    curWord = None

    inAlt = 1

    words = trans.split()
    lWords = len(words)

    # subsub gen: setting up a cluster node

    def clusterStart():
      nonlocal part
      nonlocal inAlt

      while part and part[0] in clusterChars:
        cb = part[0]
        if cb == '_':
          inAlt = 2

        cNode = yield token.node('cluster')

        curCluster[cb].append(cNode)

        yield token.feature(type=cb)
        part = part[1:]

    # subsub gen: terminating a cluster node

    def clusterEnd():
      nonlocal part
      nonlocal inAlt

      for ce in clusterChars.values():
        if ce in part:
          part = part.replace(ce, '')
          cb = clusterCharsInv[ce]
          if cb == '_':
            inAlt = 1

          for cNode in curCluster[cb]:
            yield token.terminate(cNode)
          del curCluster[cb]

    # subsub gen: setting up a sign node

    def signStart():
      yield token.slot()

      yield token.feature(
          language=inAlt,
          after=(
              '-' if p < lParts - 1 else
              ' ' if w < lWords - 1 else
              ''
          ),
      )

  # sub gen: adding data to a sign node

    def signData():
      nonlocal part

      yield token.feature(
          atf=part,
      )

      if part == '':
        errors['empty part'][src].add((i, line, word))
        return

      if part and part[0] == '{' and part[-1] == '}':
        part = part[1:-1]
        yield token.feature(super=1)

      match = graphemeRe.search(part)
      if match:
        yield token.feature(
            givengrapheme=match.group(1)
        )
        part = graphemeRe.sub('', part)

      for (mc, mf) in markChars.items():
        if mc in part:
          part = part.replace(mc, '')
          yield token.feature(**{mf: 1})

      if part == '':
        errors['empty part'][src].add((i, line, word))
      elif part.islower():
        yield token.feature(
            reading=part,
        )
      elif part.isupper():
        yield token.feature(
            grapheme=part,
        )
      else:
        errors['mixed case'][src].add((i, line, part))

    # the outer loop of the lineData sub generator

    for (w, word) in enumerate(words):

      curWord = yield token.node('word')

      word = word.replace('{', '-{').replace('}', '}-')
      word = word.strip('-')

      parts = word.split('-')
      lParts = len(parts)

      for p in range(len(parts)):
        part = parts[p]

        yield from clusterStart()
        yield from signStart()
        yield from clusterEnd()
        yield from signData()

      yield token.terminate(curWord)

    # terminating all unfinished clusters

    for cNodes in curCluster.values():
      for cNode in cNodes:
        yield token.terminate(cNode)
    curCluster.clear()

  # the outer loop of the corpus generator

  for src in sorted(sources):
    path = f'{IN_DIR}/{src}.txt'
    print(f'Reading source {src}')

    with open(path) as fh:
      inTrans = False
      i = 0
      for line in fh:
        i += 1
        if line.startswith('Transliteration:'):
          inTrans = True
          yield from tabletStart()
          continue

        elif line[0].isupper():
          inTrans = False
          continue

        elif not inTrans:
          continue

        line = line.strip()

        if line.startswith('&'):
          yield from tabletData()

          continue

        if line.startswith('@'):
          yield from faceStart()
          continue

        match = transRe.match(line)
        if not match:
          continue

        ln = match.group(1)
        trans = match.group(2)

        if curFace is None:
          yield from faceInsert('obverse')

        yield from lineStart(ln, trans)
        yield from lineData(trans)

      yield from tabletEnd()

      print(f'{src:<15} : {i:>4} : {pNum:<20}\r')

  if errors:
    showErrors(errors)


def convert():
  sources = getSources()
  token = getTokenObj()

  return token.convert(
      generateTokens(sources, token),
      slotType,
      otext=otext,
      generic=generic,
      intFeatures=intFeatures,
      featureMeta=featureMeta,
  )


# TF LOADING (to test the generated TF)

def loadTf():
  TF = Fabric(locations=[OUT_DIR])
  allFeatures = TF.explore(silent=True, show=True)
  loadableFeatures = allFeatures['nodes'] + allFeatures['edges']
  api = TF.load(loadableFeatures, silent=False)
  if api:
    print(f'max node = {api.F.otype.maxNode}')
    print('Frequency of readings')
    print(api.F.reading.freqList()[0:20])
    print('Frequency of grapheme')
    print(api.F.grapheme.freqList()[0:20])


# MAIN

good = convert()
# good = True

if good:
  loadTf()
