"""
Main script to run the application

Run in command line: python3 -m dash_src.app
"""

from dash import html, dcc
import dash

import dash_src.data_validation

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        # data stored across pages
        dcc.Store("store_file_paths",data=[]),
        dcc.Store("store_file_selected",data=[]),

        # display page
        html.H1("📚 Speed Reading Training 📖"),
        html.Div(
            [
                html.Div(
                    dcc.Link(f"{page['name']}", href=page["path"]),
                )
                for page in dash.page_registry.values()
            ]
        ),
        dash.page_container
    ]
)


if __name__ == "__main__":
    dash_src.data_validation.main()

    app.run(debug=True)
