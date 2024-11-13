import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load the data
data = pd.read_csv('medicine_data.csv')

# Create the Dash application
app = dash.Dash(__name__)

# Layout of the web application
app.layout = html.Div([
    html.H1('Interactive Medicine Dashboard'),

    # Dropdown for selecting the graph type or "All" option
    html.Div([
        html.Label('Select Graph Type or "All"'),
        dcc.Dropdown(
            id='graph_type',
            options=[
                {'label': 'Medicine Category Distribution', 'value': 'category_dist'},
                {'label': 'Price Distribution per Category', 'value': 'price_dist'},
                {'label': 'Dosage vs Price', 'value': 'dosage_price'},
                {'label': 'Quantity per Category', 'value': 'quantity'},
                {'label': 'All', 'value': 'all'},  # Option to show all graphs
            ],
            value='all',  # Default value
        )
    ]),

    # Dropdown for selecting the category filter
    html.Div([
        html.Label('Select Category'),
        dcc.Dropdown(
            id='category_filter',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in data['Category'].unique()],
            value='All',  # Default value
        )
    ]),

    # Range Slider for filtering by Price
    html.Div([
        html.Label('Filter by Price Range'),
        dcc.RangeSlider(
            id='price_range',
            min=data['Price'].min(),
            max=data['Price'].max(),
            step=1,
            marks={i: str(i) for i in range(int(data['Price'].min()), int(data['Price'].max()), 10)},
            value=[data['Price'].min(), data['Price'].max()]
        ),
    ]),

    # Divs for all graphs
    html.Div([
        html.Div([dcc.Graph(id='category_dist')], id='category_dist_div', style={'display': 'block'}),
        html.Div([dcc.Graph(id='price_dist')], id='price_dist_div', style={'display': 'block'}),
        html.Div([dcc.Graph(id='dosage_price')], id='dosage_price_div', style={'display': 'block'}),
        html.Div([dcc.Graph(id='quantity')], id='quantity_div', style={'display': 'block'}),
    ])
])

# Define the callback to update the graph based on user input
@app.callback(
    [Output('category_dist', 'figure'),
     Output('price_dist', 'figure'),
     Output('dosage_price', 'figure'),
     Output('quantity', 'figure'),
     Output('category_dist_div', 'style'),
     Output('price_dist_div', 'style'),
     Output('dosage_price_div', 'style'),
     Output('quantity_div', 'style')],
    [Input('graph_type', 'value'),
     Input('category_filter', 'value'),
     Input('price_range', 'value')]
)
def update_graph(graph_type, category_filter, price_range):
    # Filter the data based on the selected category and price range
    filtered_data = data[(data['Price'] >= price_range[0]) & (data['Price'] <= price_range[1])]
    if category_filter != 'All':
        filtered_data = filtered_data[filtered_data['Category'] == category_filter]

    # Create figures for each plot
    category_dist_fig = px.bar(filtered_data, x='Category', title='Distribution of Medicines by Category', color='Category')

    price_dist_fig = px.box(filtered_data, x='Category', y='Price', title='Price Distribution per Category')

    dosage_price_fig = px.scatter(filtered_data, x='Dosage', y='Price', color='Category', title='Dosage vs Price of Medicines')

    quantity_fig = px.pie(filtered_data.groupby('Category')['Quantity'].sum().reset_index(), names='Category', values='Quantity', title='Total Quantity of Medicines by Category')

    # Customize layout and add hover functionality
    category_dist_fig.update_traces(marker=dict(line=dict(color="black", width=1)))
    price_dist_fig.update_traces(marker=dict(line=dict(color="black", width=1)))
    dosage_price_fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    quantity_fig.update_traces(textinfo="percent+label", pull=[0.1, 0.1])

    # Set hover info
    dosage_price_fig.update_traces(marker=dict(size=12), hovertemplate='Dosage: %{x}<br>Price: %{y}<br>Category: %{marker.color}')

    # Determine which graphs to show based on the user's selection
    if graph_type == 'all':
        return category_dist_fig, price_dist_fig, dosage_price_fig, quantity_fig, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
    elif graph_type == 'category_dist':
        return category_dist_fig, {}, {}, {}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    elif graph_type == 'price_dist':
        return {}, price_dist_fig, {}, {}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif graph_type == 'dosage_price':
        return {}, {}, dosage_price_fig, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif graph_type == 'quantity':
        return {}, {}, {}, quantity_fig, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}

    return category_dist_fig, price_dist_fig, dosage_price_fig, quantity_fig, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
