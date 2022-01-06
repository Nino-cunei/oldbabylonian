import types
from tf.advanced.find import loadModule
from tf.advanced.app import App


MODIFIERS = """
    collated
    remarkable
    question
    damage
    uncertain
    missing
    excised
    supplied
""".strip().split()


def fmt_layoutRich(app, n, **kwargs):
    return app._wrapHtml(n, "r")


def fmt_layoutUnicode(app, n, **kwargs):
    return app._wrapHtml(n, "u")


class TfApp(App):
    def __init__(app, *args, **kwargs):
        atf = loadModule("atf", *args)
        atf.atfApi(app)
        app.fmt_layoutRich = types.MethodType(fmt_layoutRich, app)
        app.fmt_layoutUnicode = types.MethodType(fmt_layoutUnicode, app)
        super().__init__(*args, **kwargs)
        api = app.api
        Fall = api.Fall
        allNodeFeatures = set(Fall())
        app.modifiers = [m for m in MODIFIERS if m in allNodeFeatures]

    def _wrapHtml(app, n, kind):
        modifiers = app.modifiers
        api = app.api
        F = api.F
        Fs = api.Fs
        typ = F.type.v(n)
        after = (F.afteru.v(n) if kind == "u" else F.after.v(n)) or ""
        if typ == "empty":
            material = '<span class="empty">∅</span>'
        elif typ == "comment" or typ == "commentline":
            material = f'<span class="comment">{F.comment.v(n)}</span>'
        elif typ == "unknown":
            partR = Fs("reading" + kind).v(n) or ""
            if partR:
                partR = f'<span class="r">{partR}</span>'
            partG = Fs("grapheme" + kind).v(n) or ""
            if partG:
                partG = f'<span class="g">{partG}</span>'
            material = f'<span class="uncertain">{partR}{partG}</span>'
        elif typ == "ellipsis":
            material = f'<span class="missing">{Fs("grapheme" + kind).v(n)}</span>'
        elif typ == "reading":
            material = f'<span class="r">{Fs("reading" + kind).v(n)}</span>'
        elif typ == "grapheme":
            material = f'<span class="g">{Fs("grapheme" + kind).v(n)}</span>'
        elif typ == "numeral":
            if kind == "u":
                material = F.symu.v(n)
            else:
                part = f'<span class="r">{Fs("reading" + kind).v(n) or ""}</span>'
                partG = Fs("grapheme" + kind).v(n) or ""
                if partG:
                    partG = f'<span class="g">{partG}</span>'
                part = f"{part}{partG}"
                material = f'<span class="quantity">{F.repeat.v(n) or ""}{F.fraction.v(n) or ""}</span>⌈{part}⌉'
        elif typ == "complex":
            partR = f'<span class="r">{Fs("reading" + kind).v(n) or ""}</span>'
            partG = f'<span class="g">{Fs("grapheme" + kind).v(n) or ""}</span>'
            operator = (
                f'<span class="operator">{Fs("operator" + kind).v(n) or ""}</span>'
            )
            material = f"{partR}{operator}⌈{partG}⌉"
        else:
            material = Fs("sym" + kind).v(n)
        clses = " ".join(cf for cf in modifiers if Fs(cf).v(n))
        if clses:
            material = f'<span class="{clses}">{material}</span>'
        if F.det.v(n):
            material = f'<span class="det">{material}</span>'
        if F.langalt.v(n):
            material = f'<span class="langalt">{material}</span>'
        return f"{material}{after}"
