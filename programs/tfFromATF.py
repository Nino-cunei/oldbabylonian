import sys
import os
import re
import collections
import json
from unicodedata import name as uname
from shutil import rmtree
from glob import glob
from tf.fabric import Fabric
from tf.convert.walker import CV

# LOCATIONS

BASE = os.path.expanduser('~/github')
ORG = 'Nino-cunei'
REPO = 'oldbabylonian'
VERSION_SRC = '0.2'
VERSION_TF = '0.2'
REPO_DIR = f'{BASE}/{ORG}/{REPO}'

TRANS_DIR = f'{REPO_DIR}/sources/cdli/transcriptions'
WRITING_DIR = f'{REPO_DIR}/sources/writing'

SIGN_FILE = 'GeneratedSignList.json'
SIGN_PATH = f'{WRITING_DIR}/{SIGN_FILE}'

IN_DIR = f'{TRANS_DIR}/{VERSION_SRC}'

TF_DIR = f'{REPO_DIR}/tf'
OUT_DIR = f'{TF_DIR}/{VERSION_TF}'


#  CHARACTERS

prime = "'"
ellips = '…'

emphatic = {
    's,': 'ş',
    't,': 'ţ',
}

unknownStr = 'xX'
unknownSet = set(unknownStr)

lowerLetterStr = 'abcdefghijklmnopqrstuvwyz' + ''.join(emphatic.values())
upperLetterStr = lowerLetterStr.upper()
lowerLetterStr += prime


div = '÷'
digitStr = f'0123456789{div}'

divRe = re.compile(r'''([0-9])/([0-9])''')


def divRepl(match):
  return f'{match.group(1)}{div}{match.group(2)}'


times = '×'
excl = '¡'
graphemeStr = f'{times}{excl}'
operatorStr = '.+/:'
operatorSet = set(operatorStr)


flagging = {
    '*': 'collated',
    '!': 'remarkable',
    '?': 'question',
    '#': 'damage',
}
flagStr = ''.join(flagging)

clusterChars = (
    ('┌', '┐', '_', '_', 'alternate'),
    ('◀', '▶', '{', '}', 'determinative'),
    ('∈', '∋', '(', ')', 'uncertain'),
    ('〖', '〗', '[', ']', 'missing'),
    ('«', '»', '<<', '>>', 'supplied'),
    ('⊂', '⊃', '<', '>', 'excised'),
)
(langCabB, langCabE) = clusterChars[0][0:2]
(braceCabB, braceCabE) = clusterChars[1][0:2]
(bracketCabB, bracketCabE) = clusterChars[2][0:2]

clusterCharsB = {x[0] for x in clusterChars}
clusterCharsE = {x[1] for x in clusterChars}
clusterCharsA = {x[0] for x in clusterChars} | {x[1] for x in clusterChars}
clusterCharsO = {x[2] for x in clusterChars} | {x[3] for x in clusterChars}
clusterType = {x[0]: x[4] for x in clusterChars}
clusterAtfE = {x[0]: x[1] for x in clusterChars}
clusterAtfB = {x[1]: x[0] for x in clusterChars}
clusterAtf = {x[0]: x[2] for x in clusterChars}
clusterAtf.update({x[1]: x[3] for x in clusterChars})
clusterAtfInv = {co: ca for (ca, co) in clusterAtf.items()}

readingPat = (
    f'(?:(?:[{lowerLetterStr}{upperLetterStr}]'
    f'[{lowerLetterStr}{upperLetterStr}{digitStr}{prime}]*'
    f')|{ellips}|[{unknownStr}])'
    f'[{flagStr}]*'
)
graphemePat = (
    r'\|?'
    f'[{upperLetterStr}]'
    f'[{upperLetterStr}{digitStr}{operatorStr}]*'
    r'\|?'
)


def makeClusterEscRepl(cab, cae):
  def repl(match):
    return f'{cab}{match.group(2)}{cae}'

  return repl


clusterEscRe = {}
clusterEscRepl = {}

for (cab, cae, cob, coe, ctp) in clusterChars:
  if cob == coe:
    clusterEscRe[cab] = re.compile(f'''({re.escape(cob)}(.*?){re.escape(coe)})''')
    clusterEscRepl[cab] = makeClusterEscRepl(cab, cae)


def clusterCheck(text):
  return clusterORe.findall(text)


def transEsc(text):
  text = divRe.sub(divRepl, text)
  text = text.replace('...', ellips)
  text = text.replace('x(', f'{times}(')
  text = text.replace('!(', f'{excl}(')
  for (exp, abb) in emphatic.items():
    text = text.replace(exp, abb)
  for (cab, cae, cob, coe, ctp) in clusterChars:
    if cob == coe:
      text = clusterEscRe[cab].sub(clusterEscRepl[cab], text)
    else:
      text = text.replace(cob, cab).replace(coe, cae)
  return text


def transUnEsc(text):
  for (cab, cae, cob, coe, ctp) in clusterChars:
    text = text.replace(cab, cob).replace(cae, coe)
  for (exp, abb) in emphatic.items():
    text = text.replace(abb, exp)
  text = text.replace(excl, '!')
  text = text.replace(times, 'x')
  text = text.replace(ellips, '...')
  text = text.replace(div, '/')
  return text


def makeAscii(r):
  for (rin, rout) in transAscii.items():
    r = r.replace(rin, rout)
  return r.lower()


clusterA = re.escape(''.join(clusterCharsA))
clusterB = re.escape(''.join(clusterCharsB))
clusterE = re.escape(''.join(clusterCharsE))
clusterO = re.escape(''.join(clusterCharsO))
inside = r'''(?:\s+)'''
outside = r'''\s*'''
spaceB = r'''(?:\s+|^)'''
spaceE = r'''(?:\s+|$)'''
bO = r'\('
bC = r'\)'

insaneRe = re.compile(r'''[^0-9a-zA-Z$(){}\[\]<>.,:=$#&@"'?!/+*| _-]''')
transRe = re.compile(r'''^([0-9a-zA-Z']+)\.\s+(.+)$''')
collectionRe = re.compile(r'''^(\S+)\s+([0-9]+)\s*,?\s*([^&+]*)(?:[&+]|$)''')
commentRe = re.compile(r'∈\$(.*?)\$∋''')
numeralBackRe = re.compile(f'''(n|(?:[0-9]+(?:{div}[0-9]+)?))∈([^∋]+)∋''')
numeralRe = re.compile(f'''(n|(?:[0-9]+(?:{div}[0-9]+)?)){bO}({readingPat}){bC}''')
withGraphemeBackRe = re.compile(f'''([{graphemeStr}])∈([^∋]+)∋''')
withGraphemeRe = re.compile(f'''({readingPat})([{graphemeStr}]){bO}({graphemePat}){bC}''')
numeral2Re = re.compile(r'''([0-9]+∈[^∋]+∋)''')
clusterORe = re.compile(f'[{clusterO}]')
clusterTermRe = re.compile(f'^[{clusterA}]*$')
cSpaceBRe = re.compile(f'{outside}([{clusterB}]){inside}')
cSpaceERe = re.compile(f'{inside}([{clusterE}]){outside}')
wHyphenBRe = re.compile(f'{spaceB}([{clusterB}]*)-')
wHyphenERe = re.compile(f'-([{clusterE}]*){spaceE}')
cHyphenBRe = re.compile(f'([{clusterB}]+)-')
cHyphenERe = re.compile(f'-([{clusterE}]+)')
cFlagRe = re.compile(f'[{clusterA}]([{flagStr}]+)[{clusterA}]')
inlineCommentRe = re.compile(r'''^├[^┤]*┤$''')


# TF CONFIGURATION

slotType = 'sign'

generic = {
    'name': 'AbB Old Babylonian Cuneiform',
    'editor': 'Cale Johnson et. al.',
    'institute': 'CDL',
    'converters': 'Cale Johnson, Dirk Roorda',
}

otext = {
    'fmt:text-orig-full': '{atfpre}{atf}{atfpost}{after}',
    'fmt:text-ling-full': '{atfpre}{reading/grapheme}{atfpost}{after}',
    'fmt:text-graph-full': '{atfpre}{givengrapheme/grapheme/reading}{atfpost}{after}',
    'fmt:text-uni-full': '{atfpre}{unicode}{atfpost}{uafter}',
    'sectionFeatures': 'pnumber,face',
    'sectionTypes': 'document,face',
}

intFeatures = set('''
    langalt
    meta
    primeln
    primecol
    det
    uncertain
    srcLnNum
    trans
    volume
'''.strip().split()) | set(flagging.values())

featureMeta = {
    'after': {
        'description': 'what comes after a sign (- or space)',
    },
    'atf': {
        'description': (
            'full atf of a sign (without cluster chars)'
            ' or word (including cluster chars)'
        ),
    },
    'atfpost': {
        'description': 'atf of cluster closings at sign',
    },
    'atfpre': {
        'description': 'atf of cluster openings at sign',
    },
    'col': {
        'description': 'ATF column number',
    },
    'collated': {
        'description': 'whether a sign is collated (*)',
    },
    'collection': {
        'description': 'collection of a document',
    },
    'comment': {
        'description': '$ comment to line or inline comment to slot ($ and $) ',
    },
    'damage': {
        'description': 'whether a sign is damaged',
    },
    'det': {
        'description': 'whether a sign is a determinative (between braces)',
    },
    'docnote': {
        'description': 'additional remarks in the document identification',
    },
    'docnumber': {
        'description': 'number of a document within a collection-volume',
    },
    'face': {
        'description': 'full name of a face including the enclosing object',
    },
    'fraction': {
        'description': 'fraction of a numeral',
    },
    'givengrapheme': {
        'description': 'grapheme given in transcription by !() or x()',
    },
    'grapheme': {
        'description': 'grapheme of a sign',
    },
    'lang': {
        'description': 'language of a document',
    },
    'langalt': {
        'description': '1 if a sign is in the alternate language (i.e. Sumerian)',
    },
    'ln': {
        'description': 'ATF line number, may be $ or #, without prime',
    },
    'meta': {
        'description': 'whether a comment is meta (#) as opposed to structural ($)',
    },
    'object': {
        'description': 'name of an object of a document',
    },
    'operator': {
        'description': 'the ! or x in a !() or x() construction',
    },
    'pnumber': {
        'description': 'P number of a document',
    },
    'primecol': {
        'description': 'whether a prime is present on a column number',
    },
    'primeln': {
        'description': 'whether a prime is present on a line number',
    },
    'question': {
        'description': 'whether a sign has the question flag (?)',
    },
    'reading': {
        'description': 'reading of a sign',
    },
    'remarkable': {
        'description': 'whether a sign is remarkable (!)',
    },
    'repeat': {
        'description': 'repeat of a numeral',
    },
    'srcfile': {
        'description': 'source file name of a document',
    },
    'srcLn': {
        'description': 'full line in source file',
    },
    'srcLnNum': {
        'description': 'line number in source file',
    },
    'trans': {
        'description': 'whether a line has a translation',
    },
    'translation@en': {
        'description': 'translation of line in language en = English',
    },
    'type': {
        'description': 'name of a type of cluster or kind of sign',
    },
    'uafter': {
        'description': 'what comes after a sign when represented as unicode (space)',
    },
    'uncertain': {
        'description': 'whether a sign is between brackets ()',
    },
    'unicode': {
        'description': 'unicode representation of a sign, based on reading and grapheme',
    },
    'volume': {
        'description': 'volume of a document within a collection',
    },
}


# ATF INTERPRETATION

transUni = {
    'sz': 'š',
    's,': 'ṣ',
    "s'": 'ś',
    't,': 'ṭ',
    'h,': 'ḫ',
}

transAscii = {rout.upper(): rin for (rin, rout) in transUni.items()}

VAR_OBJ = 'object'
DEFAULT_OBJ = 'tablet'

OBJECTS = set('''
    tablet
    envelope
    case
'''.strip().split())

FACES = set('''
    obverse
    reverse
    left edge
    upper edge
    lower edge
    bottom
    surface a
    seal 1
'''.strip().split())

FACES_CORRECTION = {
    'overse': 'obverse',
    'obverrse': 'obverse',
}

COL_CORRECTION = {
    'second': 'column',
}

COMMENTS = '''
    (uninscribed)
    (needs to be added)
'''
COMMENTS = {c.strip() for c in COMMENTS.strip('\n').split('\n')}

COMMENT_PATTERN = r'''
    (?:
      ^
      (?:
          (?: maybe)?
          (?:
              (?:
                  (?:at \s+ least)
                  | about
              )?
              \s*
              (?:
                  (?:
                    [0-9]+
                    (?:-[0-9]+)?
                  )
                  | one | two | three | four | five | six | seven | eight | nine | ten

              )
              \s+
              lines?
          )
          | rest | obverse | reverse | seal |
          (?:
              beginning
              (?: \s+ lines?)?
          )
          |
          (?: blank \s+ space)
          | single | double
      )?
      \s*
      (?:
          (?:
              broken
              (?:\s+ off)?
          )
          | blank | illegible | unreadable | uninscribed | destroyed | missing | erased | effaced
          | ruling | impression |
          (?: not \s+ inscribed) |
          (?: of \s+ traces)
      )?
      $
    )
    |
    (?:
      ^
      reading
    )
'''
COMMENT_RE = re.compile(COMMENT_PATTERN, re.X)


def bracketBackRepl(match):
  return f'{match.group(1)}({match.group(2)})'


def wHyphenBRepl(match):
  return f' {match.group(1)}'


def wHyphenERepl(match):
  return f'{match.group(1)} '


def cHyphenBRepl(match):
  return f'-{match.group(1)}'


def cHyphenERepl(match):
  return f'{match.group(1)}-'


def insaneRepl(match):
  return f'┣{match.group(0)}┫'


def cSpaceBRepl(match):
  return ' ' + match.group(1)


def cSpaceERepl(match):
  return match.group(1) + ' '


commentNotes = []


def commentRepl(match):
  comment = match.group(1)
  commentIndex = len(commentNotes)
  commentNotes.append(comment.strip())
  return f'├{commentIndex}┤'


# ERROR HANDLING

def showDiags(diags, kind, batch=20):
  if not diags:
    print('No diags')
  else:
    for (diag, srcs) in sorted(diags.items()):
      print(f'{kind} {diag}')
      for (src, data) in sorted(srcs.items()):
        print(f'\t{src} ({len(data)}x)')
        for (l, line, doc, sore) in sorted(data)[0:batch]:
          soreRep = '' if sore is None else f'"{sore}" in '
          print(f'\t\t{l} in {doc}: {soreRep}{line}')
        if len(data) > batch:
          print(f'\t\t + more')


# SET UP CONVERSION

def getMapping():
  with open(SIGN_PATH) as fh:
    signs = json.load(fh)['signs']

  print(f'{len(signs)} signs in the json sign file')

  mapping = collections.defaultdict(set)

  for (sign, signInfo) in signs.items():
    uniStr = signInfo['signCunei']
    values = signInfo['values']
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


def checkSane(line):
  inSane = insaneRe.findall(line)
  insaneRep = ''
  lineMsg = line
  if inSane:
    sep = ''
    for c in sorted(inSane):
      try:
        name = uname(c)
      except ValueError:
        name = '??'
      insaneRep += f"{sep}┣{c}┫ = {ord(c):>04x} = {name}"
      sep = '; '
    lineMsg = insaneRe.sub(insaneRepl, line)
    line = insaneRe.sub('', line)
  return (insaneRep, lineMsg, line)


# DIRECTOR

def director(cv):

  sources = getSources()
  mapping = getMapping()

  curDocument = None
  recentObject = None
  curFace = None
  recentColumn = None
  curLine = None
  recentTrans = None
  curCluster = collections.defaultdict(list)
  curSign = None
  skip = False

  i = 0
  pNum = None

  pNums = {}

  warnings = collections.defaultdict(lambda: collections.defaultdict(set))
  errors = collections.defaultdict(lambda: collections.defaultdict(set))

  # sub director: setting up a document node

  def uni(reading, grapheme, sep=''):
    uReading = '|'.join(mapping.get(reading, (reading,))) if reading is not None else ''
    uGrapheme = '|'.join(mapping.get(grapheme, (grapheme,))) if grapheme is not None else ''
    result = uReading
    if grapheme:
      result += f'{sep}({uGrapheme})'
    return result

  def documentStart():
    # we build nodes for documents, faces, lines
    # the node is stored in the cur-variables
    # we remember the latest object and column specs
    # object and column is stored in the recent variables
    nonlocal curDocument
    nonlocal pNum
    nonlocal skip

    documentEnd()

    identifiers = line[1:].split('=')
    pNum = identifiers[0].strip()
    docNum = identifiers[-1].strip()

    other = pNums.get(pNum, None)
    if other is not None:
      (otherSrc, otherI) = other
      rep = f'{pNum} also in {otherSrc}:{otherI}'
      errors[f'document: duplicate pnums'][src].add((i, line, pNum, rep))
      skip = True
      return

    curDocument = cv.node('document')
    pNums[pNum] = (src, i)

    sys.stderr.write(f'{src:<15} : {i:>4} : {pNum:<20}\r')

    cv.feature(
        curDocument,
        pnumber=pNum,
        srcfile=src,
        srcLnNum=i,
        srcLn=line,
    )
    skip = False

    docnumber = None
    docnote = None
    match = collectionRe.match(docNum)

    if not match:
      warnings[f'document: malformed collection volume, number'][src].add(
          (i, line, pNum, docNum)
      )
      docnote = docNum
    else:
      collection = match.group(1)
      volume = match.group(2)
      docnumber = match.group(3).strip()
      docnote = None
      if docnumber:
        docnumber = docnumber.replace('pl. ', '').strip()
        docnumParts = docnumber.split(',', 1)
        if len(docnumParts) == 1:
          docnote = None
        else:
          docnumber = docnumParts[0].strip()
          docnote = docnumParts[1].strip()

      if ' ' in docnumber:
        warnings[f'document: unusual number'][src].add(
            (i, line, pNum, docnumber)
        )
        docnote = docnumber
        docnumber = None
      cv.feature(curDocument, collection=collection, volume=volume)

    if docnumber:
      cv.feature(curDocument, docnumber=docnumber)
    if docnote:
      cv.feature(curDocument, docnote=docnote)

  # sub director: terminating a document node

  def documentEnd():
    nonlocal curDocument
    nonlocal recentObject

    if curDocument is None:
      return

    faceEnd()
    recentObject = None
    cv.terminate(curDocument)
    if not cv.linked(curDocument):
      errors[f'document: empty'][src].add((i, line, pNum, None))
    curDocument = None

  # sub director: processing an # metadata line

  def processMeta():
    lineInfo = line[1:].strip()
    if not curDocument:
      errors[f'meta: outside document'][src].add((i, line, pNum, lineInfo))
      return
    if len(line) > 1 and line[1] == ' ':
      commentInsert(meta=True)
      return

    if lineInfo.startswith('atf:l'):
      errors[f'meta: no space after atf:'][src].add((i, line, pNum, None))
      lineInfo = 'atf: l' + lineInfo[5:]
    fields = lineInfo.split(maxsplit=1)
    if fields[0] == 'atf:':
      infoFields = fields[1].split(maxsplit=1)
      if len(infoFields) != 2:
        errors[f'meta: invalid'][src].add((i, line, pNum, fields[1]))
        return
      (key, value) = infoFields
      value = value.strip()
      if value.startswith('='):
        newValue = value[1:].strip()
        errors[f'meta: spurious ='][src].add((i, line, pNum, f'"{value}" => "{newValue}"'))
        value = newValue
      cv.feature(curDocument, **{key: value})
    elif fields[0] == 'tr.en:':
      if not curLine:
        errors[f'meta: translation outside line'][src].add((i, line, pNum, lineInfo))
        return
      cv.feature(curLine, **{'trans': 1, 'translation@en': fields[1]})
    else:
      errors[f'meta: unknown kind'][src].add((i, line, pNum, fields[0]))
      return

  # sub director: processing an @ specifier

  def processAtSpec():
    lineInfo = line[1:].strip()
    fields = lineInfo.split(maxsplit=1)
    typ = fields[0]
    subType = fields[1] if len(fields) == 2 else None

    if typ == 'column' or typ in COL_CORRECTION:
      if typ in COL_CORRECTION:
        typCorr = COL_CORRECTION[typ]
        errors[f'structure: column correction'][src].add((i, line, pNum, f'{typ} => {typCorr}'))
        typ = typCorr
      columnSet(subType)
    elif typ == 'object':
      objectSet(subType)
    elif typ in OBJECTS:
      objectSet(lineInfo)
    elif typ in FACES or typ in FACES_CORRECTION:
      if typ in FACES_CORRECTION:
        faceCorr = FACES_CORRECTION[typ]
        errors[f'structure: face correction'][src].add((i, line, pNum, f'{typ} => {faceCorr}'))
        faceStart(faceCorr)
      else:
        faceStart(lineInfo)
    else:
      errors[f'structure: unrecognized @'][src].add((i, line, pNum, lineInfo))

  # sub director: setting the object type

  def objectSet(typ):
    nonlocal recentObject
    nonlocal recentColumn

    if typ is None:
      errors[f'structure: object without type'][src].add((i, line, pNum, None))

    faceEnd()
    recentColumn = None
    recentObject = typ

  # sub director: setting up a face node

  def faceStart(faceName):
    nonlocal curFace
    nonlocal recentObject

    faceEnd()
    curFace = cv.node('face')

    if recentObject is None:
      errors[f'structure: object missing'][src].add((i, line, pNum, faceName))
      recentObject = DEFAULT_OBJ

    objSpec = recentObject if recentObject and recentObject != DEFAULT_OBJ else ''
    sep = ' - ' if objSpec and faceName else ''
    faceSpec = f'{objSpec}{sep}{faceName or ""}'
    cv.feature(
        curFace,
        object=recentObject,
        face=faceSpec,
        srcfile=src,
        srcLnNum=i,
        srcLn=line,
    )

  def faceEnd():
    nonlocal recentColumn
    nonlocal curFace

    if curFace is None:
      return

    lineEnd()
    recentColumn = None
    cv.terminate(curFace)
    if not cv.linked(curFace):
      errors[f'structure: face empty'][src].add((i, line, pNum, None))
    curFace = None

  # sub director: setting the column number

  def columnSet(number):
    nonlocal recentColumn

    if number is None:
      errors[f'structure: column without number'][src].add((i, line, pNum, None))

    lineEnd()
    recentColumn = number

  # sub director: setting up a comment line

  # comments are $ lines.
  # We interpret a comment line as a line with one empty slot.
  # The comment it self is a feature of the line node.

  def commentInsert(meta=False):
    nonlocal curLine

    lineEnd()
    curLine = cv.node('line')
    emptySlot = cv.slot()
    cv.feature(emptySlot, type='empty')

    comment = line[1:].strip()
    if not meta and comment not in COMMENTS and not COMMENT_RE.match(comment):
      warnings[f'comment: unrecognized'][src].add((i, line, pNum, comment))
    cv.feature(
        curLine,
        comment=comment,
        ln='#' if meta else '$',
        srcfile=src,
        srcLnNum=i,
        srcLn=line,
    )
    if meta:
      cv.feature(curLine, meta=1)
    if recentColumn is not None:
      cv.feature(curLine, col=recentColumn)

    cv.terminate(curLine)
    curLine = None

  # sub director: setting up a line node

  def lineStart(ln):
    nonlocal curLine
    nonlocal recentTrans

    lineEnd()
    curLine = cv.node('line')

    hasPrimeLn = "'" in ln
    if hasPrimeLn:
      ln = ln.replace("'", '')

    cv.feature(
        curLine,
        ln=ln,
        srcfile=src,
        srcLnNum=i,
        srcLn=line,
    )
    if hasPrimeLn:
      cv.feature(curLine, primeln=1)

    if recentColumn is not None:
      hasPrimeCol = "'" in recentColumn
      col = recentColumn.replace("'", '') if hasPrimeCol else recentColumn
      cv.feature(curLine, col=col)

      if hasPrimeCol:
        cv.feature(curLine, primecol=1)

    recentTrans = recentTrans.strip() + ' '

    commentNotes.clear()
    recentTrans = commentRe.sub(commentRepl, recentTrans)

    for (cab, cae, cob, coe, ctp) in clusterChars:
      bCount = recentTrans.count(cab)
      eCount = recentTrans.count(cae)
      if bCount != eCount:
        errors[f'cluster: unbalanced {cob} {coe}'][src].add(
            (i, line, pNum, f'{bCount} vs {eCount}')
        )

    changed = False
    if cSpaceBRe.search(recentTrans):
      recentTrans = cSpaceBRe.sub(cSpaceBRepl, recentTrans)
      changed = True

    if cSpaceERe.search(recentTrans):
      recentTrans = cSpaceERe.sub(cSpaceERepl, recentTrans)
      changed = True

    recentTrans = recentTrans.strip()

    if changed:
      errors[f'cluster: space near edge'][src].add((i, line, pNum, transUnEsc(recentTrans)))

  def lineEnd():
    nonlocal curLine

    if curLine is None:
      return

    cv.terminate(curLine)
    if not cv.linked(curLine):
      errors[f'line: empty'][src].add((i, line, pNum, None))
    curLine = None

  # sub director: adding data to a line node
  # this is itself a complicated generator with sub gens

  def lineData():
    nonlocal curLine
    nonlocal recentTrans

    curWord = None

    inAlt = 0
    inBrace = False
    inBracket = False

    if wHyphenBRe.search(recentTrans):
      errors[f'line: words starting with -'][src].add((i, line, pNum, None))
      recentTrans = wHyphenBRe.sub(wHyphenBRepl, recentTrans)
    if wHyphenERe.search(recentTrans):
      errors[f'line: words ending with -'][src].add((i, line, pNum, None))
      recentTrans = wHyphenERe.sub(wHyphenERepl, recentTrans)
    if cHyphenBRe.search(recentTrans):
      errors[f'line: clusters starting with -'][src].add((i, line, pNum, None))
      recentTrans = cHyphenBRe.sub(cHyphenBRepl, recentTrans)
    if cHyphenERe.search(recentTrans):
      errors[f'line: clusters ending with -'][src].add((i, line, pNum, None))
      recentTrans = cHyphenERe.sub(cHyphenERepl, recentTrans)

    words = recentTrans.split()

    # subsub director: processing cluster chars

    def clusterChar(before):
      nonlocal part
      nonlocal inAlt
      nonlocal inBrace
      nonlocal inBracket

      brackets = ''

      if cFlagRe.search(part):
        errors[f'cluster: flag enclosed in cluster chars'][src].add(
            (i, line, pNum, transUnEsc(part))
        )

      flags = ''
      while part:
        refChar = part[0] if before else part[-1]
        if refChar in flagging:
          flags += refChar
        else:
          if refChar not in clusterCharsA:
            break
          if refChar in clusterCharsB:
            cab = refChar
            cob = clusterAtf[cab]
            if before:
              brackets += cab
            else:
              brackets = cab + brackets

            if cab == langCabB:
              inAlt = 1
            elif cab == braceCabB:
              inBrace = True
            elif cab == bracketCabB:
              inBracket = True

            cNode = cv.node('cluster')

            curCluster[cab].append(cNode)

            cv.feature(cNode, type=clusterType[cab])
          elif refChar in clusterCharsE:
            cae = refChar
            cab = clusterAtfB[cae]
            coe = clusterAtf[cae]
            cob = clusterAtf[cab]
            if before:
              brackets += cae
            else:
              brackets = cae + brackets

            if cae == langCabE:
              inAlt = 0
            elif cae == braceCabE:
              inBrace = False
            elif cae == bracketCabE:
              inBracket = False

            for cNode in curCluster[cab]:
              cv.terminate(cNode)
              if not cv.linked(cNode):
                errors[f'cluster: empty {cob} {coe}'][src].add((i, line, pNum, None))
            del curCluster[cab]
        part = part[1:] if before else part[0:-1]

      if before:
        part = flags + part
      else:
        part += flags[::-1]

      return brackets

    # subsub director: finishing off  all clusters on a line

    def clusterEndMakeSure():
      for (cab, cNodes) in curCluster.items():
        cob = clusterAtf[cab]
        cae = clusterAtfE[cab]
        coe = clusterAtf[cae]
        for cNode in cNodes:
          cv.terminate(cNode)
          if not cv.linked(cNode):
            errors[f'cluster: empty {cob} {coe}'][src].add((i, line, pNum, None))
      curCluster.clear()

    # subsub director: setting up a sign node

    def signStart():
      nonlocal curSign

      curSign = cv.slot()

      if inAlt:
        cv.feature(curSign, langalt=inAlt)
      if inBrace:
        cv.feature(curSign, det=1)
      if inBracket:
        cv.feature(curSign, uncertain=1)
  # sub director: adding data to a sign node

    def doFlags():
      nonlocal part

      lPart = len(part)
      for i in range(lPart):
        refChar = part[-1]
        if refChar in flagging:
          mf = flagging[refChar]
          cv.feature(curSign, **{mf: 1})
          part = part[0:-1]
        else:
          break

    def signData(clusterBefore, clusterAfter, after):
      nonlocal curSign
      nonlocal part

      origPart = part

      uafter = None if after == '-' else after

      if after:
        cv.feature(curSign, after=after)
      if uafter:
        cv.feature(curSign, uafter=uafter)

      if clusterBefore:
        cv.feature(
            curSign,
            atfpre=transUnEsc(clusterBefore),
        )
      if clusterAfter:
        cv.feature(
            curSign,
            atfpost=transUnEsc(clusterAfter),
        )

      if not part:
        cv.feature(curSign, type='empty')
        errors['sign: empty (in cluster)'][src].add((i, line, pNum, transUnEsc(origPart)))
        return

      if part.startswith('├') and part.endswith('┤'):
        commentIndex = int(part[1:-1])
        comment = commentNotes[commentIndex]
        cv.feature(curSign, type='comment', comment=comment, atf=f'($ {comment} $)')
        return

      cv.feature(curSign, atf=transUnEsc(part))

      match = numeralRe.match(part)
      if match:
        quantity = match.group(1)
        part = match.group(2)
        doFlags()
        cv.feature(curSign, type='numeral')
        if quantity == 'n':
          fraction = None
          repeat = None
        elif div in quantity:
          fraction = transUnEsc(quantity)
          repeat = None
          cv.feature(curSign, fraction=fraction)
        else:
          repeat = int(quantity)
          fraction = None
          cv.feature(curSign, repeat=repeat)

        part = transUnEsc(part)
        unicode = (
            uni(part, None)
            if repeat is None and fraction is None else
            uni(part, None) * repeat
            if repeat is not None else
            uni(part, fraction)
        )

        if part.islower():
          cv.feature(curSign, reading=part, unicode=unicode)
        else:
          cv.feature(curSign, grapheme=part, unicode=unicode)
        return

      match = withGraphemeRe.search(part)
      if match:
        part = match.group(1)
        operator = match.group(2)
        doFlags()
        grapheme = match.group(3)

        part = transUnEsc(part)
        grapheme = transUnEsc(grapheme)
        operator = transUnEsc(operator)

        cv.feature(
            curSign,
            type='complex',
            reading=part,
            givengrapheme=grapheme,
            operator=operator,
            unicode=uni(part, grapheme),
        )
        return

      doFlags()

      if part == '':
        errors['sign: empty (after flags)'][src].add((i, line, pNum, transUnEsc(origPart)))
        cv.feature(curSign, type='empty')
        return

      if part == ellips:
        typ = 'ellipsis'
        part = transUnEsc(part)
        cv.feature(curSign, type=typ, grapheme=part)
        return

      if part in unknownSet:
        typ = 'unknown'
        part = transUnEsc(part)
        cv.feature(curSign, type=typ)
        if part.islower():
          cv.feature(curSign, reading=part)
        else:
          cv.feature(curSign, grapheme=part)
        return

      if part.islower():
        part = transUnEsc(part)
        cv.feature(curSign, type='reading', reading=part, unicode=uni(part, None))
        return

      if part.isupper():
        part = transUnEsc(part)
        cv.feature(curSign, type='grapheme', grapheme=part, unicode=uni(None, part))
        return

      part = transUnEsc(part)
      cv.feature(curSign, type='other', grapheme=part, unicode=uni(None, part))
      msg = 'mixed case' if part.isalnum() else 'strange grapheme'
      errors[f'sign: {msg}'][src].add((i, line, pNum, transUnEsc(origPart)))

    def getParts(word):
      origWord = word

      parts = []
      curPart = ''
      inSign = False
      endSign = False
      endPart = False

      while word:
        inCase = True
        if word.startswith('x'):
          c = 'x'
          word = word[1:]
        elif word.startswith(ellips):
          c = ellips
          word = word[1:]
        else:
          match = numeralRe.match(word) or withGraphemeRe.match(word)
          if match:
            c = match.group(0)
            lc = len(c)
            word = word[lc:]
          else:
            inCase = False
        if inCase:
          if endPart or endSign:
            parts.append((curPart, ''))
            curPart = c
            endPart = False
            endSign = False
          else:
            curPart += c
          inSign = True
          endSign = True
          continue

        c = word[0]
        if c == '-' or c in operatorSet:
          if inSign or len(parts) == 0:
            parts.append((curPart, c))
          else:
            (prevPart, prevAfter) = parts[-1]
            parts[-1] = (prevPart + curPart, prevAfter + c)
            errors[f'sign: {c} after no sign'][src].add(
                (i, line, pNum, transUnEsc(curPart))
            )
          curPart = ''
          inSign = False
          endSign = False
          endPart = False
        elif c in clusterCharsB:
          if inSign:
            parts.append((curPart, ''))
            curPart = c
            inSign = False
            endSign = False
            endPart = False
          else:
            curPart += c
        elif c in clusterCharsE:
          curPart += c
          if inSign:
            endPart = True
        elif c in flagging:
          if inSign and not endPart:
            curPart += c
          elif not inSign and not endPart:
            errors[f'sign: flag not attached to sign (ignored)'][src].add(
                (i, line, pNum, transUnEsc(curPart))
            )
          elif inSign:
            errors[f'sign: flag attached to cluster (applied to sign instead)'][src].add(
                (i, line, pNum, transUnEsc(curPart))
            )
            curPart += c
          else:
            errors[f'sign: flag after cluster chars (ignored)'][src].add(
                (i, line, pNum, transUnEsc(curPart))
            )
        else:
          if endPart or endSign:
            parts.append((curPart, ''))
            curPart = c
            endSign = False
            endPart = False
          else:
            curPart += c
          inSign = True
        word = word[1:]

      if curPart:
        if inSign:
          parts.append((curPart, ''))
        else:
          if len(parts):
            parts[-1] += ((curPart, ''))
          else:
            errors[f'sign: empty (in word)'][src].add(
                (i, line, pNum, f'{transUnEsc(curPart)} in {transUnEsc(origWord)}')
            )
            parts = [(curPart, '')]
      return parts

    # the outer loop of the lineData sub generator

    lWords = len(words)

    for (w, word) in enumerate(words):
      curWord = cv.node('word')
      if not inlineCommentRe.match(word):
        cv.feature(curWord, atf=transUnEsc(word))

      parts = getParts(word)
      lParts = len(parts)

      for p in range(len(parts)):
        (part, after) = parts[p]

        cAtfStart = clusterChar(True)
        signStart()
        cAtfEnd = clusterChar(False)
        after += (
            ' ' if p == lParts - 1 and w != lWords - 1 else ''
        )
        signData(cAtfStart, cAtfEnd, after)

      cv.terminate(curWord)
      if not cv.linked(curWord):
        errors[f'word: empty'][src].add((i, line, pNum, None))
      curWord = None

    # terminating all unfinished clusters

    clusterEndMakeSure()

  # the outer loop of the corpus generator

  for src in sorted(sources):
    path = f'{IN_DIR}/{src}.txt'
    print(f'Reading source {src}')

    with open(path) as fh:
      i = 0
      for line in fh:
        i += 1

        line = line.strip()

        if not line or line[0].isupper():
          continue

        isDoc = line.startswith('&')

        if isDoc:
          if len(line) > 1 and line[1] == 'P':
            documentStart()
          else:
            errors[f'atf: stray & replaced by $'][src].add((i, line, pNum, None))
            commentInsert()

        isMeta = line.startswith('#')

        if not isMeta or not line.startswith('#tr.'):
          (msg, lineMsg, line) = checkSane(line)
          if msg:
            errors[f'atf: illegal character(s)'][src].add((i, lineMsg, pNum, msg))

        if isDoc:
          continue

        if skip:
          continue

        if isMeta:
          processMeta()
          continue

        isStruct = line.startswith('@')

        if isStruct:
          processAtSpec()
          continue

        if curFace is None:
          faceStart(None)

        isComment = line.startswith('$')

        if isComment:
          commentInsert()
          continue

        isNumbered = transRe.match(line)
        if isNumbered:
          ln = isNumbered.group(1)
          recentTrans = isNumbered.group(2)
        else:
          errors[f'line: not numbered'][src].add((i, line, pNum, None))
          ln = ''
          recentTrans = line
          continue

        recentTrans = transEsc(recentTrans)
        cos = clusterCheck(recentTrans)
        if cos:
          cosRep = ' '.join(sorted(set(cos)))
          errors[f'cluster: not escaped {cosRep}'][src].add((i, line, pNum, None))

        recentTrans = numeralBackRe.sub(bracketBackRepl, recentTrans)
        recentTrans = withGraphemeBackRe.sub(bracketBackRepl, recentTrans)

        lineStart(ln)
        lineData()

      documentEnd()

      print(f'{src:<15} : {i:>4} : {pNum:<20}\r')

  print(f'\n{len(pNums)} documents in corpus')

  if warnings:
    showDiags(warnings, 'WARNING')
  if errors:
    showDiags(errors, 'ERROR')


def convert():
  cv = getConverter()

  return cv.walk(
      director,
      slotType,
      otext=otext,
      generic=generic,
      intFeatures=intFeatures,
      featureMeta=featureMeta,
      generateTf=generateTf,
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

generateTf = len(sys.argv) == 1 or sys.argv[1] != '-notf'

print(f'ATF to TF converter for {REPO}')
print(f'ATF source version = {VERSION_SRC}')
print(f'TF  target version = {VERSION_TF}')
good = convert()

if generateTf and good:
  loadTf()
