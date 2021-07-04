def applyTableStyle(df):
    styles = [
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
        dict(selector="table", props=[("width", "850px")]),
    ]
    patchingStyle = (
        df.style.set_table_styles(styles)
        .hide_index()
        .set_precision(0)
        .apply(stateName, subset=["State.Name"], axis=1)
        # .render()
    )
    return patchingStyle


def stateName(s):
    # columns = len(s)
    if "running" in s["State.Name"]:
        return ["background-color: green;"]
    elif "stopped" in s["State.Name"]:
        return ["background-color: red;"]
    else:
        return [""] * columns
