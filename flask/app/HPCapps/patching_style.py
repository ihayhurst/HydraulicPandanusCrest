import pandas as pd


def applyTableStyle(df):
    styles = [
        hover(),
        dict(
            selector="th",
            props=[
                ("font-size", "100%"),
                ("text-align", "left"),
                ("text-transform", "capitalize"),
                ("background-color", "#000033"),
            ],
        ),
        dict(selector="caption", props=[("caption-side", "bottom")]),
        dict(selector="td a", props=[("display", "block")]),
    ]
    patchingStyle = (
        df.style.applymap(colorGrade, subset=["boot-time", "days-pending"])
        .set_table_attributes('id="PatchingTable"')
        .set_precision(0)
        .apply(oldscandate, axis=1)
        .set_table_styles(styles)
        .set_properties(subset=["owner"], **{"width": "300px"})
        .set_properties(subset=["release"], **{"width": "130px"})
        .hide_index()
        .format({"days-pending": zero_pending})
        .format({"hostname": make_clickable})
        .format({"last-scan": make_human})
        .apply(endOfLife, axis=1)
        .render()
    )
    return patchingStyle


def hover(hover_color="#000033"):
    return dict(selector="tr:hover", props=[("background-color", "%s" % hover_color)])


def colorGrade(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for timedelta over specified
    strings, black otherwise.
    """
    patchingCritical = 60
    patchingUrgent = 50
    if val >= patchingCritical:
        color = "red"
    elif val >= patchingUrgent:
        color = "orange"
    else:
        color = "white"
    return f"color: {color}"


def endOfLife(s):
    columns = len(s)
    if "- EOL" in s["updates"]:
        return ['font-style: italic;color: white']*columns
    else:
        return ['']*columns


def oldscandate(s):
    """
    Takes a scalar and returns string for each column
    the css property `'color: rgba(r,g,b,alpha)'` for scandate >2
    otherwise empty string '' for each column
    """
    columns = len(s)
    if s["last-scan"] >=7:
        return ['color: rgba(128,128,255,0.7)']*columns
    else:
        return ['']*columns


def make_clickable(val):
    return f'<a href="/inventory/{val}" class="button">{val}</a>'


def make_human(val):
    if val == 0:
        return 'Today'
    else:
        return val


def zero_pending(val):
    if val == 0:
        return "n/a"
    else:
        return val
