import streamlit as st
from streamlit.components.v1.components import CustomComponent
from code_editor import code_editor
from functools import partial
import base64
import zlib
import requests
import urllib.parse


def encoder(string: str) -> str:
    """
    https://docs.kroki.io/kroki/setup/encode-diagram/#python
    """
    return base64.urlsafe_b64encode(zlib.compress(string.encode("utf-8"), 9)).decode(
        "ascii"
    )


def decoder(string: str) -> str:
    return zlib.decompress(base64.urlsafe_b64decode(string)).decode("utf8")


def get_customized_code_editor(lang: str = "python") -> CustomComponent:
    """
    https://code-editor-documentation.streamlit.app/Advanced_usage
    """
    keyboard_binding = st.selectbox("Keyboard Binding", ["vim", "vscode"])

    # css to inject related to info bar
    css_string = """
    background-color: #bee1e5;

    body > #root .ace-streamlit-dark~& {
    background-color: #262830;
    }

    .ace-streamlit-dark~& span {
    color: #fff;
    opacity: 0.6;
    }

    span {
    color: #000;
    opacity: 0.5;
    }

    .code_editor-info.message {
    width: inherit;
    margin-right: 75px;
    order: 2;
    text-align: center;
    opacity: 0;
    transition: opacity 0.7s ease-out;
    }

    .code_editor-info.message.show {
    opacity: 0.6;
    }

    .ace-streamlit-dark~& .code_editor-info.message.show {
    opacity: 0.5;
    }
    """
    # create info bar dictionary
    info_bar = {
        "name": "language info",
        "css": css_string,
        "style": {
            "order": "1",
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "center",
            "width": "100%",
            "height": "2.5rem",
            "padding": "0rem 0.75rem",
            "borderRadius": "8px 8px 0px 0px",
            "zIndex": "9993",
        },
        "info": [{"name": lang, "style": {"width": "100px"}}],
    }
    buttons = [
        {
            "name": "Copy",
            "feather": "Copy",
            "hasText": True,
            "alwaysOn": True,
            "commands": [
                "copyAll",
                [
                    "infoMessage",
                    {
                        "text": "Copied to clipboard!",
                        "timeout": 2500,
                        "classToggle": "show",
                    },
                ],
            ],
            "style": {"right": "0.4rem"},
        },
        # {
        #     "name": "Copy",
        #     "feather": "Copy",
        #     "hasText": True,
        #     "alwaysOn": True,
        #     "commands": ["copyAll"],
        #     "style": {"top": "0.46rem", "right": "0.4rem"},
        # },
        # {
        #     "name": "Shortcuts",
        #     "feather": "Type",
        #     "class": "shortcuts-button",
        #     "hasText": True,
        #     "commands": ["toggleKeyboardShortcuts"],
        #     "style": {"bottom": "calc(50% + 1.75rem)", "right": "0.4rem"},
        # },
        # {
        #     "name": "Collapse",
        #     "feather": "Minimize2",
        #     "hasText": True,
        #     "commands": [
        #         "selectall",
        #         "toggleSplitSelectionIntoLines",
        #         "gotolinestart",
        #         "gotolinestart",
        #         "backspace",
        #     ],
        #     "style": {"bottom": "calc(50% - 1.25rem)", "right": "0.4rem"},
        # },
        # {
        #     "name": "Save",
        #     "feather": "Save",
        #     "hasText": True,
        #     "commands": ["save-state", ["response", "saved"]],
        #     "response": "saved",
        #     "style": {"bottom": "calc(50% - 4.25rem)", "right": "0.4rem"},
        # },
        {
            "name": "Run",
            "feather": "Play",
            "primary": True,
            "hasText": True,
            "showWithIcon": True,
            "commands": ["submit"],
            "style": {"bottom": "0.44rem", "right": "0.4rem"},
        },
        # {
        #     "name": "Command",
        #     "feather": "Terminal",
        #     "primary": True,
        #     "hasText": True,
        #     "commands": ["openCommandPallete"],
        #     "style": {"bottom": "3.5rem", "right": "0.4rem"},
        # },
    ]

    return partial(
        code_editor,
        lang="text",
        shortcuts=keyboard_binding,
        height=[5, 30],
        buttons=buttons,
        info=info_bar,
    )


def kroki_api(
    kroki_endpoint: str, graph_type: str, image_type: str, content: str, **kwargs
) -> requests.Response:
    """
    kwargs is to accept dummy inputs
    """
    # https://stackoverflow.com/questions/8223939/how-to-join-absolute-and-relative-urls
    uri = urllib.parse.urljoin(
        kroki_endpoint, "/".join([graph_type, image_type, encoder(content)])
    )
    return requests.get(uri)


if __name__ == "__main__":
    print(decoder(encoder("digraph G {Hello->World}")))
    svg = kroki_api("https://kroki.io/", "graphviz", "svg", "digraph G {Hello->World}")
    print(svg.text)
    png = kroki_api("https://kroki.io/", "graphviz", "png", "digraph G {Hello->World}")
