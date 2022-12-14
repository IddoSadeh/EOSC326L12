import re
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_daq as daq
from flask import Flask
import plotly.express as px
from skimage import io

# build app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# lab2 figure
fig1 = go.Figure()
# lab2 figure
fig2 = go.Figure()

# lab2 instructions
instructions1 = open("instructions1.md", "r")
instructions1_markdown = instructions1.read()

# lab2 instructions
instructions2 = open("instructions2.md", "r")
instructions2_markdown = instructions2.read()

# clsoing instructions
instructions3 = open("instructions3.md", "r")
instructions3_markdown = instructions3.read()

# configure options modebars for annotating
config = {
    # 'editable': True,
    # # more edits options: https://dash.plotly.com/dash-core-components/graph
    'displayModeBar': True,
    'edits': {
        'annotationPosition': False,
        'annotationText': True,
    },
    "modeBarButtonsToAdd": [
        "drawline",
        "eraseshape",


    ],
    "modeBarButtonsToRemove": [
        "zoom",
        "Pan",
        "select2d",
        "lasso2d",
        "zoomin",
        "zoomout",
        "autoscale",
        "resetscale",
        "addtext",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
    ],

}

img1 = io.imread("https://www.eoas.ubc.ca/~quest/sketching/agerange-exercise1.jpg")

fig1 = px.imshow(img1)
fig1.update_layout(
    autosize=False,
    width=1000 * 0.7,
    height=680 * 0.7,
)
fig1.update_xaxes(
    fixedrange=True
)
fig1.update_yaxes(
    fixedrange=True
)
fig1.layout.shapes = None
fig1.layout.annotations = None

img2 = io.imread("https://www.eoas.ubc.ca/~quest/sketching/agerange-exercise2.jpg")


fig2 = px.imshow(img2)

fig2.update_layout(
    autosize=False,
    width=1000 * 0.7,
    height=680 * 0.7,

)
fig2.update_xaxes(
    fixedrange=True
)
fig2.update_yaxes(
    fixedrange=True
)
fig2.layout.shapes = None
fig2.layout.annotations = None

app.layout = html.Div(
    [
        dcc.Store(id='shapes_data1', storage_type='session'),
        dcc.Store(id='text_data1', storage_type='session'),
        dcc.Store(id='shapes_data2', storage_type='session'),
        dcc.Store(id='text_data2', storage_type='session'),
        html.Div([
            # instructions for lab 1
            dcc.Markdown(
                children=instructions1_markdown,

            ),
        ]),
        # lab 1 image
        html.Div(
            [
                dcc.Graph(
                    id="fig1-image", figure=fig1, config=config
                ),
                daq.ColorPicker(
                    id="color-picker1", label="Color Picker", value=dict(rgb=dict(r=0, g=0, b=0, a=0)), size=164,

                )
            ],
            style={
                "display": "flex",
            },
        ),
        # instructions for lab 2
        html.Div([
            dcc.Markdown(
                children=instructions2_markdown,
                dangerously_allow_html=True
            ),
        ], style={
            "display": "block",
        }
        ),

        # lab 2 image
        html.Div(
            [
                dcc.Graph(
                    id="fig2-image", figure=fig2, config=config
                ),
                daq.ColorPicker(
                    id="color-picker2", label="Color Picker", value=dict(rgb=dict(r=0, g=0, b=0, a=0)), size=164,

                )
            ],
            style={
                "display": "flex",
            },
        ),

        html.Div(
            # tips and reminders
            dcc.Markdown(
                children=instructions3_markdown,
                dangerously_allow_html=True
            ),
        ),
        html.Div(id='dummy_div'),

    ],

)


@app.callback(
    Output('fig1-image', 'figure'),
    Output('shapes_data1', 'data'),
    Output('text_data1', 'data'),
    Input('fig1-image', 'relayoutData'),
    Input("color-picker1", "value"),
    Input('shapes_data1', 'data'),
    Input('text_data1', 'data'),


)
def change_color1(relayout1_data, color, shapes_data, text_data):

    if shapes_data is None and text_data is None:
        fig1.layout.shapes = None
        fig1.layout.annotations = None
        fig1.add_annotation(x=100, y=300,
                            text="Enter your name",
                            showarrow=False,
                            )
        fig1.add_annotation(x=100, y=320,
                            text="Enter your student number",
                            showarrow=False,
                            )
        return fig1, None, fig1.layout.annotations
    else:
        fig1.layout.shapes = shapes_data
        fig1.layout.annotations = text_data
    if ctx.triggered_id == "color-picker1":
        update_annotations1(relayout1_data, color)
    elif'dragmode' in str(relayout1_data):
        return dash.no_update
    else:
        update_annotations1(relayout1_data)
    return fig1,fig1.layout.shapes, fig1.layout.annotations


def update_annotations1(relayout_data, color_value='black', size=14):
    if color_value != 'black':
        r = color_value['rgb']['r']
        g = color_value['rgb']['g']
        b = color_value['rgb']['b']
        a = color_value['rgb']['a']
    else:
        r, g, b, a = 0, 0, 0, 0
    # for shape layouts
    # https://plotly.com/python/reference/layout/shapes/#layout-shapes-items-shape-type
    if "'shapes':" in str(relayout_data):
        if len(relayout_data['shapes']) == 0:
            fig1.layout.shapes = ()
        else:
            if 'hex' in str(color_value):
                relayout_data['shapes'][-1]["line"]["color"] = color_value["hex"]
            fig1.layout.shapes = ()
            # all shapes on screen will be returned in relay data upon new shape creation.
            for i in relayout_data['shapes']:
                fig1.add_shape(i)
    # changing shapes
    elif "shapes[" in str(relayout_data):

        # using regex to find which shape was changed
        shape_num_index = re.search(r"\d", str(relayout_data))
        i = int(str(relayout_data)[shape_num_index.start()])

        # changing dictionary keys so we can update the shape change easily
        dictnames = list(relayout_data.keys())
        new_dict = {}
        counter = 0
        for name in dictnames:
            dictnames[counter] = name[10:]
            counter = counter + 1
        for key, n_key in zip(relayout_data.keys(), dictnames):
            new_dict[n_key] = relayout_data[key]
        if 'hex' in str(color_value):
            new_dict["line"] = dict(color=color_value["hex"])
        fig1.update_shapes(new_dict, i)
    else:
        fig1.update_annotations(captureevents=True)
        # using regex to find which annotation was changed
        if relayout_data is None:
            j = len(fig1.layout.annotations) - 1
            fig1.update_annotations(Annotation(fig1.layout.annotations[j]['x'], fig1.layout.annotations[j]['y'],
                                               fig1.layout.annotations[j]['text'], f'rgba({r},{g},{b},1)',
                                               size).__dict__,
                                    j)

        else:
            anno_num_index = re.search(r"\d", str(relayout_data))
            if anno_num_index is not None:
                i = int(str(relayout_data)[anno_num_index.start()])

                # if text content is changed "text" will be in relay data
                if "text" in str(relayout_data):
                    fig1.update_annotations(Annotation(fig1.layout.annotations[i]['x'], fig1.layout.annotations[i]['y'],
                                                       relayout_data[f'annotations[{i}].text'], f'rgba({r},{g},{b},1)',
                                                       size).__dict__,
                                            i)
                # for case where annotation was added but not changed (moved or editied)

                # if text is just moved relay data wont have "text" in data
                else:
                    fig1.update_annotations(
                        Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                                   fig1.layout.annotations[i]['text'], f'rgba({r},{g},{b},1)', size).__dict__, i)


@app.callback(
    Output('fig2-image', 'figure'),
    Output('shapes_data2', 'data'),
    Output('text_data2', 'data'),
    Input('fig2-image', 'relayoutData'),
    Input("color-picker2", "value"),
    Input('shapes_data2', 'data'),
    Input('text_data2', 'data'),

)
def change_color2(relayout2_data, color,shapes_data, text_data):

    if shapes_data is None and text_data is None:
        fig2.layout.shapes = None
        fig2.layout.annotations = None
        fig2.add_annotation(x=100, y=300,
                            text="Enter your name",
                            showarrow=False,
                            )
        fig2.add_annotation(x=100, y=320,
                            text="Enter your student number",
                            showarrow=False,
                            )
        return fig2, None, fig2.layout.annotations
    else:
        fig2.layout.shapes = shapes_data
        fig2.layout.annotations = text_data
    if ctx.triggered_id == "color-picker2":
        update_annotations2(relayout2_data, color)
    elif 'dragmode' in str(relayout2_data):
        return dash.no_update
    else:
        update_annotations2(relayout2_data)
    return fig2, fig2.layout.shapes, fig2.layout.annotations


def update_annotations2(relayout_data, color_value='black', size=14):
    if color_value != 'black':
        r = color_value['rgb']['r']
        g = color_value['rgb']['g']
        b = color_value['rgb']['b']
        a = color_value['rgb']['a']
    else:
        r, g, b, a = 0, 0, 0, 0
    # for shape layouts
    # https://plotly.com/python/reference/layout/shapes/#layout-shapes-items-shape-type
    if "'shapes':" in str(relayout_data):
        if len(relayout_data['shapes']) == 0:
            fig2.layout.shapes = ()
        else:
            if 'hex' in str(color_value):
                relayout_data['shapes'][-1]["line"]["color"] = color_value["hex"]
            fig2.layout.shapes = ()
            # all shapes on screen will be returned in relay data upon new shape creation.
            for i in relayout_data['shapes']:
                fig2.add_shape(i)
    # changing shapes
    elif "shapes[" in str(relayout_data):

        # using regex to find which shape was changed
        shape_num_index = re.search(r"\d", str(relayout_data))
        i = int(str(relayout_data)[shape_num_index.start()])

        # changing dictionary keys so we can update the shape change easily
        dictnames = list(relayout_data.keys())
        new_dict = {}
        counter = 0
        for name in dictnames:
            dictnames[counter] = name[10:]
            counter = counter + 1
        for key, n_key in zip(relayout_data.keys(), dictnames):
            new_dict[n_key] = relayout_data[key]
        if 'hex' in str(color_value):
            new_dict["line"] = dict(color=color_value["hex"])
        fig2.update_shapes(new_dict, i)
    else:
        fig2.update_annotations(captureevents=True)
        # using regex to find which annotation was changed
        if relayout_data is None:
            j = len(fig2.layout.annotations) - 1
            fig2.update_annotations(Annotation(fig2.layout.annotations[j]['x'], fig2.layout.annotations[j]['y'],
                                               fig2.layout.annotations[j]['text'], f'rgba({r},{g},{b},1)',
                                               size).__dict__,
                                    j)

        else:
            anno_num_index = re.search(r"\d", str(relayout_data))
            if anno_num_index is not None:
                i = int(str(relayout_data)[anno_num_index.start()])

                # if text content is changed "text" will be in relay data
                if "text" in str(relayout_data):
                    fig2.update_annotations(Annotation(fig2.layout.annotations[i]['x'], fig2.layout.annotations[i]['y'],
                                                       relayout_data[f'annotations[{i}].text'], f'rgba({r},{g},{b},1)',
                                                       size).__dict__,
                                            i)
                # for case where annotation was added but not changed (moved or editied)

                # if text is just moved relay data wont have "text" in data
                else:
                    fig2.update_annotations(
                        Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                                   fig2.layout.annotations[i]['text'], f'rgba({r},{g},{b},1)', size).__dict__, i)


class Annotation:
    def __init__(self, x, y, text, color, size):
        self.x = x
        self.y = y
        self.text = text
        self.font = dict(
            family="Courier New, monospace",
            size=size,
            color=color,

        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
