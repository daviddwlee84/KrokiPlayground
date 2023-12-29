from typing import Literal
import streamlit as st
import utils
import os
from glob import glob
import config
from io import BytesIO

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.session_state.kroki_endpoint = st.text_input("Kroki Endpoint", "https://kroki.io/")

"""
# Kroki Playground
"""

with st.expander("Kroki Cheatsheet"):
    st.image(
        "https://kroki.io/assets/kroki_cheatsheet_20210515_v1.1_EN.jpeg",
        caption="Kroki Cheatsheet",
    )

mode: Literal["From Demo", "Manual"] = st.selectbox("Mode", ["From Demo", "Manual"])


def get_graph_type(path: str) -> str:
    return os.path.basename(os.path.dirname(path))


if mode == "From Demo":
    example_file = st.selectbox(
        "Example",
        glob(os.path.join(curr_dir, "examples/*/*")),
        format_func=lambda x: f"{get_graph_type(x)}/{os.path.basename(x)}",
    )
    # https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
    # extension = os.path.splitext(example_file)[1].strip(".")
    # graph_type = config.extension_compiler_map[extension]

    graph_type = get_graph_type(example_file)

    image_type: Literal["svg", "png", "jpeg", "pdf", "txt", "base64"] = st.selectbox(
        "Image Type",
        # config.extension_image_support[extension]
        config.graph_image_support[graph_type],
    )
    st.caption("Note that: svg is always supported.")

    with open(example_file, "r") as fp:
        example = fp.read()

else:
    graph_type: Literal["GraphViz", "Mermaid"] = st.selectbox(
        "Graph Type", ["GraphViz", "Mermaid"]
    )

    if candidates := glob(os.path.join(curr_dir, "examples", graph_type, "*")):
        example_file = candidates[0]

        image_type: Literal[
            "svg", "png", "jpeg", "pdf", "txt", "base64"
        ] = st.selectbox("Image Type", config.graph_image_support[graph_type])

        with open(example_file, "r") as fp:
            example = fp.read()

    else:
        example = ""


code_editor = utils.get_customized_code_editor(lang=graph_type)
result_value = code_editor(example)

kroki_config = {
    "kroki_endpoint": st.session_state.kroki_endpoint,
    "graph_type": graph_type.lower(),
    "image_type": image_type,
    "content": result_value.get("text"),
    "encode": utils.encoder(result_value.get("text")),
}

with st.expander("Raw Debug"):
    st.write(result_value)
    st.write(kroki_config)

if result_value.get("type") == "submit":
    response = utils.kroki_api(**kroki_config)
    if image_type == "svg":
        st.image(response.text)
    else:
        st.image(BytesIO(response.content))
