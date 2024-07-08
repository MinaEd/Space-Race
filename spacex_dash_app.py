import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

# Load SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()
launch_sites = spacex_df['Launch Site'].unique()

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for launch sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites],
        value='ALL',
        placeholder="Select a launch site",
        searchable=True
    ),
    html.Br(),
  
    # Pie chart for success launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
  
    # Range slider for payload
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        marks={i: f'{i} kg' for i in range(int(min_payload), int(max_payload) + 1, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
  
    # Scatter chart for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Pie chart for all sites
        fig = px.pie(spacex_df, names='Launch Site', title='Total Success Launches for All Sites', color='Launch Site')
    else:
        # Pie chart for a specific site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class', title=f'Success Launches for {entered_site}', color='class')
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Payload vs. Outcome for All Sites' if entered_site == 'ALL' else f'Payload vs. Outcome for site {entered_site}')
    
    # Update x-axis range to include up to 10,000 kg
    fig.update_xaxes(range=[0, 10000])
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8053)
