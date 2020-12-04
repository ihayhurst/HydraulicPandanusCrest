def applyTableStyle(df):
    styles = [
        dict(
            selector="th",
            props=[
                ("font-size", "110%"),
                ("text-align", "left"),
                ("text-transform", "capitalize"),
                ("background-color", "#000033"),
            ],
        ),
        dict(selector="caption", props=[("caption-side", "bottom")]),
        dict(selector="td a", props=[("display", "block")]),
    ]
    patchingStyle = (
         df.style.set_table_styles(styles)
        .hide_index()
        .set_precision(0)
        .render()
    )
    return patchingStyle
