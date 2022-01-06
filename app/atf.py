import types


def atfApi(app):
    app.getSource = types.MethodType(getSource, app)


def getSource(app, node, nodeType=None, lineNumbers=False):
    api = app.api
    F = api.F
    L = api.L
    sourceLines = []
    lineNumber = ""
    if lineNumbers:
        lineNo = F.srcLnNum.v(node)
        lineNumber = f"{lineNo:>5} " if lineNo else ""
    sourceLine = F.srcLn.v(node)
    if sourceLine:
        sourceLines.append(f"{lineNumber}{sourceLine}")
    for child in L.d(node, otype=nodeType):
        sourceLine = F.srcLn.v(child)
        lineNumber = ""
        if sourceLine:
            if lineNumbers:
                lineNumber = f"{F.srcLnNum.v(child):>5}: "
            sourceLines.append(f"{lineNumber}{sourceLine}")
    return sourceLines
