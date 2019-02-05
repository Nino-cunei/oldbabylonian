import sys
import os
import re
import collections
import json
from shutil import rmtree
from glob import glob
from tf.fabric import Fabric
from tf.convert.walker import CV

# LOCATIONS

BASE = os.path.expanduser('~/github')
ORG = 'Nino-cunei'
REPO = 'oldbabylonian'
VERSION_SRC = '0.2'
VERSION_TF = '0.3'
REPO_DIR = f'{BASE}/{ORG}/{REPO}'

TRANS_DIR = f'{REPO_DIR}/sources/cdli/transcriptions'
WRITING_DIR = f'{REPO_DIR}/sources/writing'

SIGN_FILE = 'GeneratedSignList.json'
SIGN_PATH = f'{WRITING_DIR}/{SIGN_FILE}'

IN_DIR = f'{TRANS_DIR}/{VERSION_SRC}'

TF_DIR = f'{REPO_DIR}/tf'
OUT_DIR = f'{TF_DIR}/{VERSION_TF}'


# ATF INTERPRETATION

clusterChars = {
    '_': '_',
    '<': '>',
    '[': ']',
}
clusterCharsInv = {ce: cb for (cb, ce) in clusterChars.items()}

markChars = {
    '+': 'combined',
    '*': 'collated',
    '!': 'exclamation',
    '?': 'uncertain',
    '#': 'damage',
}

transUni = {
    'sz': 'š',
    's,': 'ṣ',
    "s'": 'ś',
    't,': 'ṭ',
    'h,': 'ḫ',
}

transAscii = {rout.upper(): rin for (rin, rout) in transUni.items()}


def makeAscii(r):
  for (rin, rout) in transAscii.items():
    r = r.replace(rin, rout)
  return r.lower()


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
        'description': 'name of a face of a tablet or type of cluster or sign',
    },
    'subtype': {
        'description': 'additional qualification of a face of a tablet',
    },
    'atf': {
        'description': 'full atf of a sign',
    },
    'repeat': {
        'description': 'repeat of a numeral',
    },
    'fraction': {
        'description': 'fraction of a numeral',
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
    'collated': {
        'description': 'whether a sign is collated',
    },
    'combined': {
        'description': 'whether a sign is combined',
    },
    'givengrapheme': {
        'description': 'grapheme given in transcription by !()',
    },
    'comment': {
        'description': 'comment to line: material between ($ and $) ',
    },
}


# ATF PATTERNS

transRe = re.compile(r'''^([0-9a-zA-Z'.])+\s+(.*)$''')
commentRe = re.compile(r'\(\$(.*?)\$\)''')
numeralRe = re.compile(r'''([0-9]+(?:/[0-9]+)?)\(([^)]+)\)''')
graphemeRe = re.compile(r'''([a-z]+[0-9]*)(!?)\(([^)]+)\)''')
graphemexRe = re.compile(r'''\(([^)]+)\)''')
hyphRe = re.compile(r'''-+''')
numeral2Re = re.compile(r'''([0-9]+\([^)]+\))''')
stickyNumeralRe = re.compile(r'''((?:[0-9]+\([^)]+\)){2,})''')
clusterTermRe = re.compile(f'^[{re.escape("".join(clusterChars.values()))}]*$')


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

def getMapping():
  with open(SIGN_PATH) as fh:
    signs = json.load(fh)['signs']

  print(f'{len(signs)} signs in the json sign file')

  mapping = collections.defaultdict(set)

  for (sign, signData) in signs.items():
    uniStr = signData['signCunei']
    values = signData['values']
    for value in values:
      valueAscii = makeAscii(value)
      mapping[valueAscii].add(uniStr)

  print(f'{len(mapping)} distinct values in table')

  return mapping


def getSources():
  if os.path.exists(OUT_DIR):
    rmtree(OUT_DIR)
  os.makedirs(OUT_DIR, exist_ok=True)

# list all sources

  return tuple(
      os.path.splitext(os.path.basename(f))[0]
      for f in glob(f'{IN_DIR}/*.txt')
  )


def getConverter():
  TF = Fabric(locations=OUT_DIR)
  return CV(TF)


# DIRECTOR

def director(cv):

  sources = getSources()
  mapping = getMapping()

  curTablet = None
  curFace = None
  curLine = None
  curCluster = collections.defaultdict(list)
  curSign = None

  i = 0
  pNum = None

  pNums = {}

  errors = collections.defaultdict(lambda: collections.defaultdict(set))

  # sub director: setting up a tablet node

  def uni(reading, grapheme):
    uReading = '|'.join(mapping.get(reading, (reading,)))
    uGrapheme = '|'.join(mapping.get(grapheme, (grapheme,)))
    result = uReading
    if grapheme:
      result += f'({uGrapheme})'
    return result

  def tabletStart():
    nonlocal curTablet
    nonlocal curFace
    nonlocal curLine

    cv.terminate(curLine)
    curLine = None
    cv.terminate(curFace)
    curFace = None
    cv.terminate(curTablet)
    curTablet = cv.node('tablet')
    for cNodes in curCluster.values():
      for cNode in curCluster:
        cv.terminate(cNode)
    curCluster.clear()

  # sub director: adding data to a tablet node

  def tabletData():
    nonlocal pNum

    pNum = line[1:].split()[0]

    other = pNums.get(pNum, None)
    if other is not None:
      (otherSrc, otherI) = other
      rep = f'{pNum} also in {otherSrc}:{otherI}'
      errors[f'duplicate pnums'][src].add((i, line, rep))

      cv.terminate(curTablet)
      return

    pNums[pNum] = (src, i)

    sys.stderr.write(f'{src:<15} : {i:>4} : {pNum:<20}\r')

    cv.feature(
        curTablet,
        pnumber=pNum,
        srcfile=src,
        srcln=i,
        srcline=line,
    )

  # sub director: terminating a tablet node

  def tabletEnd():
    nonlocal curTablet
    nonlocal curFace
    nonlocal curLine
    cv.terminate(curLine)
    curLine = None
    cv.terminate(curFace)
    curFace = None
    cv.terminate(curTablet)
    curTablet = None

  # sub director: setting up a face node

  def faceStart():
    fields = line[1:].split(maxsplit=1)
    typ = fields[0]
    if typ == 'tablet':
      return

    faceInsert(typ)

    if len(fields) == 2:
      cv.feature(
          curFace,
          subtype=fields[1],
      )

  # sub director: inserting a default face node if no face is specified

  def faceInsert(typ):
    nonlocal curFace

    cv.terminate(curFace)
    curFace = cv.node('face')

    cv.feature(
        curFace,
        type='obverse',
        srcfile=src,
        srcln=i,
        srcline=line,
    )

  # sub director: setting up a line node

  def lineStart(ln, trans, comment):
    nonlocal curLine

    cv.terminate(curLine)
    curLine = cv.node('line')

    cv.feature(
        curLine,
        ln=ln,
        srcfile=src,
        srcln=i,
        srcline=line,
    )
    if comment is not None:
      cv.feature(
          curLine,
          comment=comment,
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

  # sub director: adding data to a line node
  # this is itself a complicated generator with sub gens

  def lineData(trans):
    nonlocal curLine

    curWord = None

    inAlt = 1

    words = trans.split()
    lWords = len(words)

    # subsub director: setting up a cluster node

    def clusterStart():
      nonlocal part
      nonlocal inAlt

      while part and part[0] in clusterChars:
        cb = part[0]
        if cb == '_':
          inAlt = 2

        cNode = cv.node('cluster')

        curCluster[cb].append(cNode)

        cv.feature(
            cNode,
            type=cb,
        )
        part = part[1:]

    # subsub director: terminating a cluster node

    def clusterEnd():
      nonlocal part
      nonlocal inAlt

      if part == '':
        return

      for ce in clusterChars.values():
        if ce in part:
          part = part.replace(ce, '')
          cb = clusterCharsInv[ce]
          if cb == '_':
            inAlt = 1

          for cNode in curCluster[cb]:
            cv.terminate(cNode)
          del curCluster[cb]

    # subsub director: setting up a sign node

    def signStart():
      nonlocal curSign

      curSign = cv.slot()

      cv.feature(
          curSign,
          language=inAlt,
          after=(
              '-' if p < lParts - 1 else
              ' ' if w < lWords - 1 else
              ''
          ),
      )

  # sub director: adding data to a sign node

    def signData():
      nonlocal curSign
      nonlocal part

      cv.feature(
          curSign,
          atf=part,
      )

      if part and part[0] == '{' and part[-1] == '}':
        part = part[1:-1]
        cv.feature(
            curSign,
            super=1,
        )

      match = graphemeRe.search(part)
      if match:
        excl = match.group(2)
        if not excl:
          errors['missing ! in front of ()'][src].add((i, line, part))

        part = match.group(1)
        grapheme = match.group(3)

        cv.feature(
            curSign,
            type='reading',
            reading=part,
            givengrapheme=grapheme,
            unicode=uni(part, grapheme),
        )

      for (mc, mf) in markChars.items():
        if mc in part:
          part = part.replace(mc, '')
          cv.feature(
              curSign,
              **{mf: 1},
          )

      if part == '':
        errors['empty part'][src].add((i, line, word))
        cv.feature(
            curSign,
            type='empty',
        )
        return

      match = numeralRe.match(part)
      if match:
        quantity = match.group(1)
        rest = match.group(2)
        cv.feature(
            curSign,
            type='numeral',
        )
        if '/' in quantity:
          fraction = quantity
          repeat = None
          cv.feature(
              curSign,
              fraction=quantity,
          )
        else:
          repeat = quantity
          fraction = None
          cv.feature(
              curSign,
              repeat=repeat,
          )

        unicode = uni(rest, None) * repeat if repeat is not None else uni(rest, fraction)

        if rest.islower():
          cv.feature(
              curSign,
              reading=rest,
              unicode=unicode,
          )
        else:
          cv.feature(
              curSign,
              grapheme=rest,
              unicode=unicode,
          )
        return

      match = graphemexRe.search(part)
      if match:
        part = match.group(1)
        cv.feature(
            curSign,
            uncertain=1,
        )
        if part == 'x' or part == '...':
          cv.feature(
              curSign,
              type='empty' if part == '...' else 'unknown',
              grapheme=part,
          )
        elif part.isupper():
          cv.feature(
              curSign,
              type='grapheme',
              grapheme=part,
          )
        elif part.islower():
          cv.feature(
              curSign,
              type='reading',
              reading=part,
              unicode=uni(part, None)
          )
        else:
          cv.feature(
              curSign,
              type='other',
              grapheme=part,
          )
        return

      part = part.replace('(', '').replace(')', '')

      if part == 'x' or part == 'X' or part == '...':
        cv.feature(
            curSign,
            type='empty' if part == '...' else 'unknown',
            grapheme=part,
        )
        return

      if part.islower():
        cv.feature(
            curSign,
            type='reading',
            reading=part,
            unicode=uni(part, None)
        )
        return

      if part.isupper():
        cv.feature(
            curSign,
            type='grapheme',
            grapheme=part,
            unicode=uni(None, part)
        )
        return

      cv.feature(
          curSign,
          type='other',
          grapheme=part,
          unicode=uni(None, part)
      )
      msg = 'mixed case' if part.isalnum() else 'strange grapheme'
      errors[msg][src].add((i, line, part))

    # the outer loop of the lineData sub generator

    for (w, word) in enumerate(words):

      curWord = cv.node('word')

      word = word.replace('{', '-{').replace('}', '}-')
      word = word.replace('[', '-[').replace(']', ']-')
      word = word.replace('<', '-<').replace('>', '>-')
      word = word.strip('-')

      parts = hyphRe.split(word)
      lParts = len(parts)

      for p in range(len(parts)):
        part = parts[p]
        if part == '':
          continue

        clusterStart()

        noMaterial = clusterTermRe.match(part)

        if not noMaterial:
          signStart()
        clusterEnd()
        if not noMaterial:
          signData()

      cv.terminate(curWord)
      curWord = None

    # terminating all unfinished clusters

    for cNodes in curCluster.values():
      for cNode in cNodes:
        cv.terminate(cNode)
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
          tabletStart()
          continue

        elif line[0].isupper():
          inTrans = False
          continue

        elif not inTrans:
          continue

        line = line.strip()

        if line.startswith('&'):
          tabletData()
          continue

        if line.startswith('@'):
          faceStart()
          continue

        match = transRe.match(line)
        if not match:
          continue

        ln = match.group(1)
        trans = match.group(2)
        comment = None

        match = commentRe.match(trans)
        if match:
          comment = match.group(1).strip()
          trans = commentRe.sub('', trans).strip()

        if curFace is None:
          faceInsert('obverse')

        lineStart(ln, trans, comment)
        lineData(trans)

      tabletEnd()

      print(f'{src:<15} : {i:>4} : {pNum:<20}\r')

  if errors:
    showErrors(errors)


def convert():
  cv = getConverter()

  return cv.walk(
      director,
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

if good:
  loadTf()
