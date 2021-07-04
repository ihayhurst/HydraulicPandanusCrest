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
        df.style.applymap(colorGrade, subset=["days-pending"])
        .applymap(rebootAdvised, subset=["boot-time"])
        .set_precision(0)
        .apply(oldscandate, axis=1)
        .set_table_styles(styles)
        .set_properties(subset=["owner"], **{"width": "300px"})
        .set_properties(subset=["release"], **{"width": "130px"})
        .hide_index()
        .hide_columns(["critical"])
        .format({"days-pending": zero_pending})
        .format({"hostname": make_clickable})
        .format({"last-scan": make_human})
        .apply(endOfLife, axis=1)
        # .render()
    )
    return patchingStyle


def rebootAdvised(val):
    if val >= 120:
        color = "#CF6679"
    else:
        color = "white"
    return f"color: {color}"


def hover(hover_color="#000033"):
    return dict(selector="tr:hover", props=[("background-color", "%s" % hover_color)])


def colorGrade(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for timedelta over specified
    strings, black otherwise.
    """
    Critical = 60
    Urgent = 50
    if val >= Critical:
        color = "#CF6679"
    elif val >= Urgent:
        color = "orange"
    else:
        color = "white"
    return f"color: {color}"


def endOfLife(s):
    columns = len(s)
    if "- EOL" in s["updates"]:
        return ["font-style: italic;"] * columns
    else:
        return [""] * columns


def oldscandate(s):
    """
    Takes a scalar and returns string for each column
    the css property `'color: rgba(r,g,b,alpha)'` for scandate >2
    otherwise empty string '' for each column
    """
    columns = len(s)
    if s["last-scan"] >= 7:
        return ["color: rgba(204,134,253,0.7)"] * columns
    else:
        return [""] * columns


def make_clickable(val):
    return f'<a href="/inventory/{val}" class="button">{val}</a>'


def make_human(val):
    if val == 0:
        return "Today"
    else:
        return val


def zero_pending(val):
    if val == 0:
        return "n/a"
    else:
        return val
