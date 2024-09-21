# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")  # Adjust the file path as needed
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Generate dropdown options dynamically from unique launch sites in the DataFrame
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown list for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # Label for the RangeSlider
    html.P("Payload range (Kg):"),

    # RangeSlider for selecting payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 11000, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Pie chart to show the total successful launches count
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    # Scatter chart to show correlation between payload and success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),

    html.Br(),
])

# Define the callback to update the pie chart based on dropdown and RangeSlider input
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_pie_chart(entered_site, payload_range):
    # Filter the DataFrame based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If ALL sites are selected
    if entered_site == 'ALL':
        success_df = filtered_df[filtered_df['class'] == 1]
        success_counts = success_df['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']

        fig = px.pie(
            success_counts,
            names='Launch Site',
            values='Success Count',
            title='Total Success Launches for All Sites'
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Success and Failure Launches for site {entered_site}',
            labels={'class': 'Launch Outcome'}
        )

    return fig

# Define the callback to update the scatter plot based on dropdown and RangeSlider input
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, payload_range):
    # Filter the DataFrame based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If ALL sites are selected
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        # Filter the DataFrame for the selected launch site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {entered_site}'
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8070)
