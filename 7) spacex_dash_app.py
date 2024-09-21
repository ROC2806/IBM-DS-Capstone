# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # Dropdown list to select Launch Site
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                ),
    
    html.Br(),
    
    # Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),
    
    # Slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0',
                           2500: '2500',
                           5000: '5000',
                           7500: '7500',
                           10000: '10000'},
                    value=[min_payload, max_payload]),
    
    # Scatter chart for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback function for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected site
    filtered_df = spacex_df

    if entered_site == 'ALL':
        success_df = filtered_df[filtered_df['class'] == 1]
        success_count_by_site = success_df.groupby('Launch Site').size().reset_index(name='count')
        total_successes = success_count_by_site['count'].sum()
        success_count_by_site['percentage'] = (success_count_by_site['count'] / total_successes) * 100
        fig = px.pie(
            success_count_by_site,
            names='Launch Site',
            values='percentage',
            title='Total Success Launches By Site',
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_failure_count = site_df['class'].value_counts().reset_index(name='count')
        success_failure_count.columns = ['class', 'count']
        total_launches = success_failure_count['count'].sum()
        success_failure_count['percentage'] = (success_failure_count['count'] / total_launches) * 100
        fig = px.pie(
            success_failure_count,
            names='class',
            values='percentage',
            title=f'Total Success Launches for site {entered_site}',
        )
    
    return fig

# Callback function for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, payload_range):
    filtered_df = spacex_df.copy()
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) &
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs. Success for {selected_site}' if selected_site != 'ALL' else 'Payload vs. Success for All Sites',
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

