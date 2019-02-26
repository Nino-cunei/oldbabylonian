import collections
import re

LIMIT = 20

FLAGS = (
    ('damage', '#'),
    ('remarkable', '!'),
    ('written', ('!(', ')')),
    ('uncertain', '?'),
)

CLUSTER_BEGIN = {'[': ']', '<': '>', '(': ')', '_': '_'}
CLUSTER_END = {y: x for (x, y) in CLUSTER_BEGIN.items()}
CLUSTER_KIND = {'[': 'uncertain', '(': 'properName', '<': 'supplied'}
CLUSTER_BRACKETS = dict((name, (bOpen, CLUSTER_BEGIN[bOpen]))
                        for (bOpen, name) in CLUSTER_KIND.items())
VAR_OBJ = 'object'
DEFAULT_OBJ = 'tablet'

OBJECTS = set('''
    tablet
    envelope
    case
'''.strip().split())

FACES = {x.strip() for x in '''
    obverse
    reverse
    left
    left edge
    left side
    upper edge
    lower edge
    bottom
    surface a
    seal
    seal 1
    seal 2
'''.strip().split('\n')}

FACES_CORRECTION = {
}

COL_CORRECTION = {
    #  'second': 'column',
}

transRe = re.compile(r'''^([0-9][0-9a-zA-Z'.]*)\s+(.+)$''')


def processAtSpec(line):
  lineInfo = line[1:].strip()
  fields = lineInfo.split(maxsplit=1)
  typ = fields[0]
  subType = fields[1] if len(fields) == 2 else None

  if typ == 'column' or typ in COL_CORRECTION:
    if typ in COL_CORRECTION:
      typCorr = COL_CORRECTION[typ]
      typ = typCorr
    return ('column', subType)

  if typ == 'object':
    return ('object', subType)

  elif typ in OBJECTS:
    return ('object', lineInfo)

  if lineInfo in FACES or typ in FACES_CORRECTION:
    if lineInfo in FACES_CORRECTION:
      faceCorr = FACES_CORRECTION[lineInfo]
      return ('face', faceCorr)
    return ('face', lineInfo)

  return (None, lineInfo)


class Compare(object):
  def __init__(self, api, sourceDir, sourceFiles, tempDir):
    self.api = api
    self.sourceDir = sourceDir
    self.sourceFiles = sourceFiles
    self.tempDir = tempDir
    self.inventory()

  def inventory(self):
    hasLines = collections.Counter()
    documents = collections.Counter()
    faceTypes = set()
    usedFaces = set()

    for src in self.sourceFiles:
      curDocument = None
      curObj = None
      curFace = None
      curColumn = None
      path = f'{self.sourceDir}/{src}.txt'
      with open(path) as fh:
        for (ln, line) in enumerate(fh):
          line = line.rstrip()
          if line.startswith('&'):
            curColumn = None
            curFace = None
            curObj = None
            curDocument = line[1:].split('=', 1)[0].strip()
            documents[curDocument] += 1
          elif line.startswith('@'):
            (kind, value) = processAtSpec(line)
            if kind == 'column':
              curColumn = value
            elif kind == 'face' or kind is None:
              curColumn = None
              curFace = value
              usedFaces.add(curFace)
            elif kind == 'object':
              curColumn = None
              curFace = None
              curObj = value
          elif line.startswith('$') or transRe.match(line):
            faceRep = curFace or ''
            objSpec = curObj if curObj and curObj != DEFAULT_OBJ else ''
            sep = ' - ' if objSpec and curFace else ''
            faceSpec = f'{objSpec}{sep}{faceRep}'
            faceTypes.add(faceSpec)
            columnRep = curColumn or ''
            hasLines[curDocument] += 1
            hasLines[f'{curDocument}:{faceSpec}'] += 1
            hasLines[f'{curDocument}:{faceSpec}:{columnRep}'] += 1

    self.documents = documents
    self.hasLines = hasLines
    self.faceTypes = faceTypes
    print(f'FACES:')
    for ft in sorted(faceTypes):
      print(f'\t{ft}')
    if usedFaces != FACES | set(FACES_CORRECTION):
      for f in sorted(usedFaces - (FACES | set(FACES_CORRECTION))):
        print(f'UNRECOGNIZED FACE: {f}')
      for f in sorted((FACES | set(FACES_CORRECTION)) - usedFaces):
        print(f'UNUSED FACE: {f}')

    self.empty = {t for t in documents if not hasLines[t]}
    print(f'EMPTY TABLETS ({len(self.empty)}):')
    for t in sorted(self.empty):
      print(f'\t{t}')

  def readCorpora(self):
    seen = set()
    for src in self.sourceFiles:
      curDocument = None
      curObj = None
      curFace = None
      curColumn = None
      path = f'{self.sourceDir}/{src}.txt'
      with open(path) as fh:
        for (ln, line) in enumerate(fh):
          line = line.rstrip()
          if line.startswith('&'):
            if curDocument:
              seen.add(curDocument)
            curFace = None
            curColumn = None
            curObj = None
            curDocument = line[1:].split('=', 1)[0].strip()
            if curDocument not in seen and self.hasLines[curDocument]:
              yield (src, curDocument, None, None, ln + 1, line)
          elif line.startswith('@'):
            (kind, value) = processAtSpec(line)
            if kind == 'column':
              curColumn = value
            elif kind == 'face':
              curColumn = None
              curFace = value
            elif kind == 'object':
              curColumn = None
              curFace = None
              curObj = value
          elif line.startswith('#') and len(line) > 1 and line[1] != ' ':
            yield (src, curDocument, None, None, ln + 1, line)
          elif line.startswith('$') or line.startswith('#') or transRe.match(line):
            faceRep = curFace or ''
            objSpec = curObj if curObj and curObj != DEFAULT_OBJ else ''
            sep = ' - ' if objSpec and curFace else ''
            faceSpec = f'{objSpec}{sep}{faceRep}'
            columnRep = curColumn or ''
            if (
                curDocument not in seen
            ):
              yield (src, curDocument, faceSpec, columnRep, ln + 1, line)

  def checkSanity(self, headers, grepFunc, tfFunc, leeway=0):
    def equalLeeway(tfTuple, grepTuple):
      if not leeway:
        return tfTuple == grepTuple

      tfRest = tfTuple[0:2] + tfTuple[3:]
      grepRest = grepTuple[0:2] + grepTuple[3:]
      tfLn = tfTuple[2]
      grepLn = grepTuple[2]
      theDiff = abs(grepLn - tfLn)
      if theDiff > leeway:
        return False
      else:
        return tfRest == grepRest

    resultTf = tuple(tfFunc())
    resultGrep = tuple(grepFunc(self.readCorpora()))

    resultHeaders = '''
        srcfile
        tablet
        ln
    '''.strip().split()
    resultHeaders.extend(headers)
    print(self._resultItem('HEAD', resultHeaders))

    firstDiff = -1
    lTf = len(resultTf)
    lGrep = len(resultGrep)
    minimum = min((lTf, lGrep))
    maximum = max((lTf, lGrep))
    equal = True
    n = 0
    while n < minimum:
      if not equalLeeway(resultTf[n], resultGrep[n]):
        equal = False
        break
      n += 1
    good = False
    if equal and minimum == maximum:
      print(f'IDENTICAL: all {maximum} items')
      self._printResult('=', resultTf)
      good = True
    else:
      firstDiff = n
      print(
          'DIFFERENT: first different item is at position'
          f' {firstDiff + 1} in the list'
      )
      if firstDiff:
        self._printResult('=', resultTf[0:firstDiff], last=True)

      self._printResultLine('TF', resultTf, firstDiff)
      self._printResultLine('GREP', resultGrep, firstDiff)

      if firstDiff >= maximum - 1:
        print('\tno more items')
      else:
        print(
            f'remaining items (TF: {lTf - firstDiff - 1});'
            f' GREP: {lGrep - firstDiff - 1}'
        )
        for k in range(firstDiff + 1, firstDiff + LIMIT):
          if k >= maximum:
            print(f'{"":<5} no more items')
            break
          if k < lTf and k < lGrep and resultTf[k] == resultGrep[k]:
            self._printResultLine('=', resultTf, k)
          else:
            self._printResultLine('TF', resultTf, k)
            self._printResultLine('GREP', resultGrep, k)
        if k < maximum - 1:
          print(f'{"TF":<5} and {lTf - k} more')
          print(f'{"GREP":<5} and {lGrep - k} more')
    print(f'Number of results: TF {len(resultTf)}; GREP {len(resultGrep)}')
    return good

  def _printResult(self, prefix, result, last=False):
    if last:
      if len(result) > LIMIT:
        print(f'{prefix:<5} start with {len(result) - LIMIT} items')
      print(
          '\n'.join(
              self._resultItem(prefix, r) for r in result[-LIMIT:]
          )
      )
    else:
      print(
          '\n'.join(
              self._resultItem(prefix, r) for r in result[0:LIMIT]
          )
      )
      if len(result) > LIMIT:
        print(f'{prefix:<5} and {len(result) - LIMIT} more')
      else:
        print(f'{prefix:<5} no more items')

  def _printResultLine(self, prefix, result, ln):
      if ln >= len(result):
          print(f'{prefix:<5}: no line present')
      else:
          print(self._resultItem(prefix, result[ln]))

  def _resultItem(self, prefix, result):
      return f'{prefix:<5}: {" ◆ ".join(str(r) for r in result)}'
