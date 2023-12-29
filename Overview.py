from typing import Literal
import streamlit as st
import utils
import os
from glob import glob
import config
from io import BytesIO

curr_dir = os.path.dirname(os.path.abspath(__file__))

"""
# Kroki Playground
"""

with st.expander("Kroki Cheatsheet"):
    st.image(
        "https://kroki.io/assets/kroki_cheatsheet_20210515_v1.1_EN.jpeg",
        caption="Kroki Cheatsheet",
    )

example_file = st.selectbox(
    "Example",
    glob(os.path.join(curr_dir, "examples/*/*")),
    format_func=lambda x: f"{os.path.basename(os.path.dirname(x))}/{os.path.basename(x)}",
)
# https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
extension = os.path.splitext(example_file)[1].strip(".")

st.session_state.kroki_endpoint = st.text_input("Kroki Endpoint", "https://kroki.io/")
image_type: Literal["svg", "png"] = st.selectbox(
    "Image Type", config.extension_image_support[extension]
)
st.caption("Note that: svg is always supported.")

code_editor = utils.get_customized_code_editor()
with open(example_file, "r") as fp:
    example = fp.read()

result_value = code_editor(example, lang=extension)

kroki_config = {
    "kroki_endpoint": st.session_state.kroki_endpoint,
    "graph_type": config.extension_compiler_map[extension],
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
