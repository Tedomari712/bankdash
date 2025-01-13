# Import required libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import os

# Initialize the app
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.FLATLY,
        'https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap'
    ]
)

# This is important for Render deployment
server = app.server

# Custom CSS
app.index_string = '''<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                font-family: 'Bebas Neue', sans-serif;
            }
            .regular-text {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            .card-body p, .card-body text {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            .card {
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>'''

# Monthly data
monthly_data = pd.DataFrame({
    'Month': ['January', 'February', 'March', 'April', 'May', 'June', 
             'July', 'August', 'September', 'October', 'November', 'December'],
    'Transactions': [8, 6, 3, 2, 0, 3239, 6147, 7311, 5853, 9986, 11574, 8217],
    'Volume': [0.00, 200.00, 200.00, 100.00, 0.00, 164960577.05, 344641363.80, 
               441605577.75, 333896656.06, 612844465.61, 660334518.30, 523575404.54],
    'Success_Rate': [0.00, 16.67, 0.00, 50.00, 0.00, 76.97, 82.43, 85.21, 
                     79.07, 84.20, 78.33, 86.84],
    'Unique_Remitters': [0, 0, 0, 0, 0, 1179, 2337, 2845, 2422, 3561, 3784, 3367],
    'Unique_Recipients': [0, 1, 0, 1, 0, 1669, 3076, 3265, 2704, 4139, 4366, 3858]
})

# Failure data
failure_data = pd.DataFrame({
    'Reason': ['General Failure', 'Limit Exceeded', 'Invalid Credit Party', 
               'Insufficient Balance', 'SOAP Error', 'Timed Out', 'System Error',
               'Connectivity Error', 'Invalid Account', 'Invalid Details', 'Other'],
    'Total': [754, 26, 223, 4219, 0, 1286, 0, 11, 1174, 430, 1193],
    'Percentage': [8.09, 0.28, 2.39, 45.29, 0.00, 13.80, 0.00, 0.12, 12.60, 4.62, 12.81]
})

# Daily data
daily_data = pd.DataFrame({
    'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'Volume': [460648034.00, 408886317.00, 437438130.00, 472289677.00, 
               649350891.00, 368343059.00, 284902756.00],
    'Count': [6340, 5291, 5486, 6128, 9313, 5901, 4571]
})

# Hourly data
hourly_data = pd.DataFrame({
    'Hour': [
        '12:00:00 AM', '12:30:00 AM', '1:00:00 AM', '1:30:00 AM', '2:00:00 AM', '2:30:00 AM',
        '3:00:00 AM', '3:30:00 AM', '4:00:00 AM', '4:30:00 AM', '5:00:00 AM', '5:30:00 AM',
        '6:00:00 AM', '6:30:00 AM', '7:00:00 AM', '7:30:00 AM', '8:00:00 AM', '8:30:00 AM',
        '9:00:00 AM', '9:30:00 AM', '10:00:00 AM', '10:30:00 AM', '11:00:00 AM', '11:30:00 AM'
    ],
    'Volume': [
        31422733.80, 34824950.20, 37178383.70, 39343104.80, 33641452.40, 32227031.80,
        34648925.80, 32454662.20, 42374824.70, 43128807.70, 46059732.10, 57139036.40,
        58015932.50, 62236995.30, 60833204.50, 55974572.20, 77837841.00, 67626737.50,
        84461058.30, 75435087.40, 67624749.70, 79260334.80, 76847398.60, 73021931.70
    ],
    'Count': [
        438, 449, 517, 510, 450, 418, 441, 469, 546, 574, 633, 774,
        820, 815, 843, 789, 1026, 980, 1131, 1095, 1020, 1120, 1067, 1045
    ]
})

# Country data
country_data = pd.DataFrame({
    'Country': ['CAN', 'CDIV', 'FIN', 'GBR', 'KEN', 'NED', 'NGA', 'SGP', 'USA', 'Unknown'],
    'Volume': [131969949.47, 1970077.63, 746691.00, 1263989309.40, 109322547.12,
               5637919.32, 5409823.55, 8871333.09, 1348601980.70, 203331985.30],
    'Count': [2544, 75, 8, 20520, 1753, 19, 590, 129, 15011, 2304],
    'Market_Share': [4.28, 0.06, 0.02, 41.04, 3.55, 0.18, 0.18, 0.29, 43.79, 6.60]
})

# Client data
client_data = pd.DataFrame({
    'Client': ['Lemfi', 'Nala', 'DLocal', 'Wapipay', 'EBanx', 'Vigipay', 'Fincra'],
    'Volume': [2686506229.61, 23023985.63, 353927405.68, 18400642.19, 
               200.00, 100.00, 300.00],
    'Transactions': [38712, 286, 3928, 99, 1, 1, 3],
    'Market_Share': [87.17, 0.75, 11.48, 0.60, 0.00, 0.00, 0.00]
})

# Define the layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1(
                "2024 Mobile Wallet Transfer Analysis", 
                className="text-primary text-center mb-4",
                style={'letterSpacing': '2px'}
            )
        ])
    ]),

    # Key Metrics Cards
    dbc.Row([
        # Total Transactions Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Annual Transactions", className="card-title text-center"),
                    html.H2(
                        f"{monthly_data['Transactions'].sum():,.0f}", 
                        className="text-primary text-center"
                    ),
                    html.P([
                        html.Span("Active Months: ", className="regular-text"),
                        html.Span(
                            f"{len(monthly_data[monthly_data['Transactions'] > 0])}",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ]),
        
        # Success Rate Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Average Success Rate", className="card-title text-center"),
                    html.H2([
                        f"{monthly_data[monthly_data['Success_Rate'] > 0]['Success_Rate'].mean():.1f}",
                        html.Small("%", className="text-muted")
                    ], className="text-primary text-center"),
                    html.P([
                        html.Span("Peak: ", className="regular-text"),
                        html.Span(
                            f"{monthly_data['Success_Rate'].max():.1f}%",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ]),
        
        # Total Volume Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Volume (KES)", className="card-title text-center"),
                    html.H2(
                        f"{monthly_data['Volume'].sum()/1e9:.2f}B", 
                        className="text-primary text-center"
                    ),
                    html.P([
                        html.Span("Monthly Average: ", className="regular-text"),
                        html.Span(
                            f"KES {(monthly_data[monthly_data['Volume'] > 0]['Volume'].mean()/1e6):,.0f}M",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ]),

        # Unique Users Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Unique Users", className="card-title text-center"),
                    html.H2(
                        f"{monthly_data['Unique_Remitters'].sum():,.0f}", 
                        className="text-primary text-center"
                    ),
                    html.P([
                        html.Span("Recipients: ", className="regular-text"),
                        html.Span(
                            f"{monthly_data['Unique_Recipients'].sum():,.0f}",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ])
    ], className="mb-4"),

    # Monthly Trends
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Monthly Transaction Analysis"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                name='Volume',
                                x=monthly_data['Month'],
                                y=monthly_data['Volume']/1e6,
                                marker_color='rgba(26, 118, 255, 0.8)',
                                yaxis='y'
                            ),
                            go.Scatter(
                                name='Success Rate',
                                x=monthly_data['Month'],
                                y=monthly_data['Success_Rate'],
                                mode='lines+markers',
                                marker=dict(
                                    size=8,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                line=dict(
                                    width=2,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                yaxis='y2'
                            )
                        ]).update_layout(
                            title='Monthly Volume and Success Rate Trends',
                            yaxis=dict(
                                title='Volume (KES Millions)',
                                titlefont=dict(color='rgba(26, 118, 255, 0.8)'),
                                tickfont=dict(color='rgba(26, 118, 255, 0.8)')
                            ),
                            yaxis2=dict(
                                title='Success Rate (%)',
                                titlefont=dict(color='rgba(255, 128, 0, 0.8)'),
                                tickfont=dict(color='rgba(255, 128, 0, 0.8)'),
                                overlaying='y',
                                side='right',
                                range=[0, 100]
                            ),
                            height=400,
                            margin=dict(l=50, r=50, t=50, b=30),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            )
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="mb-4"),

    # Success Rate Gauge and Geographic Distribution
    dbc.Row([
        # Success Rate Gauge
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Success Rate Performance"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(
                            go.Indicator(
                                mode="gauge+number",
                                value=monthly_data[monthly_data['Success_Rate'] > 0]['Success_Rate'].mean(),
                                title={"text": "Average Success Rate",
                                       "font": {"size": 16},
                                       "align": "center"},
                                number={"suffix": "%",
                                       "font": {"size": 28}},
                                gauge={
                                    'axis': {'range': [0, 100]},
                                    'bar': {'color': "#006400"},
                                    'steps': [
                                        {'range': [0, 50], 'color': 'rgba(0, 100, 0, 0.2)'},
                                        {'range': [50, 75], 'color': 'rgba(0, 100, 0, 0.4)'},
                                        {'range': [75, 100], 'color': 'rgba(0, 100, 0, 0.6)'}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 2},
                                        'thickness': 0.75,
                                        'value': monthly_data[monthly_data['Success_Rate'] > 0]['Success_Rate'].mean()
                                    }
                                }
                            )
                        ).update_layout(
                            height=300,
                            margin=dict(l=30, r=30, t=30, b=30)
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=4),
        
        # Geographic Distribution
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Geographic Distribution"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(
                            go.Pie(
                                labels=country_data['Country'],
                                values=country_data['Volume'],
                                textinfo='label+percent',
                                hole=0.3,
                                hovertemplate="<b>%{label}</b><br>" +
                                            "Volume: KES %{value:,.2f}<br>" +
                                            "Share: %{percent}<extra></extra>"
                            )
                        ).update_layout(
                            title='Transaction Volume by Country',
                            height=300,
                            margin=dict(l=50, r=50, t=50, b=30),
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.1
                            )
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=8)
    ], className="mb-4"),

    # Failure Analysis and Daily Patterns
    dbc.Row([
        # Failure Analysis
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Failure Analysis"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(
                            go.Treemap(
                                labels=failure_data['Reason'],
                                parents=[''] * len(failure_data),
                                values=failure_data['Total'],
                                textinfo='label+value+percent parent',
                                hovertemplate=(
                                    "<b>%{label}</b><br>" +
                                    "Count: %{value}<br>" +
                                    "Percentage: %{percentParent:.1%}<extra></extra>"
                                ),
                                marker=dict(
                                    colors=failure_data['Total'],
                                    colorscale=[[0, '#ffebee'], [1, '#c62828']],
                                    showscale=True
                                )
                            )
                        ).update_layout(
                            title='Transaction Failure Distribution',
                            height=400,
                            margin=dict(l=20, r=20, t=50, b=20)
                        )
                    ),
                    html.Div([
                        html.P([
                            "Total Failed Transactions: ",
                            html.Span(
                                f"{failure_data['Total'].sum():,}",
                                className="text-danger"
                            )
                        ], className="mb-0 mt-3 regular-text text-center")
                    ])
                ])
            ], className="shadow-sm")
        ], width=6),

        # Daily Transaction Pattern
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Daily Transaction Pattern"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                name='Volume',
                                x=daily_data['Day'],
                                y=daily_data['Volume']/1e6,
                                marker_color='rgba(26, 118, 255, 0.8)',
                                yaxis='y'
                            ),
                            go.Scatter(
                                name='Transactions',
                                x=daily_data['Day'],
                                y=daily_data['Count'],
                                mode='lines+markers',
                                marker=dict(
                                    size=8,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                line=dict(
                                    width=2,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                yaxis='y2'
                            )
                        ]).update_layout(
                            title='Daily Transaction Patterns',
                            yaxis=dict(
                                title='Volume (KES Millions)',
                                titlefont=dict(color='rgba(26, 118, 255, 0.8)'),
                                tickfont=dict(color='rgba(26, 118, 255, 0.8)')
                            ),
                            yaxis2=dict(
                                title='Number of Transactions',
                                titlefont=dict(color='rgba(255, 128, 0, 0.8)'),
                                tickfont=dict(color='rgba(255, 128, 0, 0.8)'),
                                overlaying='y',
                                side='right'
                            ),
                            height=400,
                            margin=dict(l=50, r=50, t=50, b=30),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            )
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=6)
    ], className="mb-4"),

    # Hourly Transaction Pattern
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Hourly Transaction Pattern"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Scatter(
                                x=hourly_data['Hour'],
                                y=hourly_data['Volume']/1e6,
                                mode='lines+markers',
                                name='Volume',
                                marker=dict(
                                    size=6,
                                    color='rgba(26, 118, 255, 0.8)'
                                ),
                                line=dict(
                                    width=2,
                                    color='rgba(26, 118, 255, 0.8)'
                                ),
                                yaxis='y'
                            ),
                            go.Scatter(
                                x=hourly_data['Hour'],
                                y=hourly_data['Count'],
                                mode='lines+markers',
                                name='Transaction Count',
                                marker=dict(
                                    size=6,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                line=dict(
                                    width=2,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                yaxis='y2'
                            )
                        ]).update_layout(
                            title='Hourly Volume and Transaction Count Distribution',
                            xaxis_title='Hour of Day',
                            yaxis=dict(
                                title='Volume (KES Millions)',
                                titlefont=dict(color='rgba(26, 118, 255, 0.8)'),
                                tickfont=dict(color='rgba(26, 118, 255, 0.8)')
                            ),
                            yaxis2=dict(
                                title='Number of Transactions',
                                titlefont=dict(color='rgba(255, 128, 0, 0.8)'),
                                tickfont=dict(color='rgba(255, 128, 0, 0.8)'),
                                overlaying='y',
                                side='right'
                            ),
                            height=350,
                            margin=dict(l=50, r=50, t=50, b=100),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            ),
                            xaxis=dict(
                                tickangle=-45,
                                tickmode='array',
                                ticktext=hourly_data['Hour'],
                                tickvals=list(range(len(hourly_data)))
                            )
                        )
                    ),
                    html.Div([
                        html.P([
                            "Peak Volume Hour: ",
                            html.Span(
                                f"{hourly_data.loc[hourly_data['Volume'].idxmax(), 'Hour']} ",
                                className="text-success"
                            ),
                            html.Span(
                                f"(KES {hourly_data['Volume'].max()/1e6:.1f}M)",
                                className="text-muted"
                            )
                        ], className="mb-0 mt-3 regular-text text-center")
                    ])
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="mb-4"),

    # Client Analysis
    dbc.Row([
        # Client Market Share
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Client Market Share"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(
                            data=[go.Pie(
                                labels=client_data['Client'],
                                values=client_data['Market_Share'],
                                textinfo='label+percent',
                                hole=0.4,
                                marker=dict(
                                    colors=[
                                        'rgb(82, 109, 255)', 
                                        'rgb(255, 99, 71)', 
                                        'rgb(32, 178, 170)', 
                                        'rgb(255, 159, 64)',
                                        'rgb(153, 102, 255)', 
                                        'rgb(255, 99, 132)',
                                        'rgb(75, 192, 192)'
                                    ]
                                ),
                                hovertemplate=(
                                    "<b>%{label}</b><br>" +
                                    "Market Share: %{value:.1f}%<br>" +
                                    "<extra></extra>"
                                )
                            )]
                        ).update_layout(
                            title='Market Share Distribution',
                            height=400,
                            margin=dict(l=20, r=20, t=50, b=20),
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.1
                            )
                        )
                    ),
                    html.Div([
                        html.P([
                            "Dominant Client: ",
                            html.Span(
                                f"{client_data.loc[client_data['Market_Share'].idxmax(), 'Client']} ",
                                className="text-success"
                            ),
                            html.Span(
                                f"({client_data['Market_Share'].max():.1f}% market share)",
                                className="text-muted"
                            )
                        ], className="mb-0 mt-3 regular-text text-center")
                    ])
                ])
            ], className="shadow-sm")
        ], width=6),

        # Client Performance
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Client Transaction Analysis"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                name='Transactions',
                                x=client_data['Client'],
                                y=client_data['Transactions'],
                                marker_color='rgba(26, 118, 255, 0.8)',
                                yaxis='y',
                                hovertemplate=(
                                    "<b>%{x}</b><br>" +
                                    "Transactions: %{y:,.0f}<br>" +
                                    "<extra></extra>"
                                )
                            )
                        ]).update_layout(
                            title='Transaction Volume by Client',
                            yaxis_title='Number of Transactions',
                            height=400,
                            margin=dict(l=50, r=50, t=50, b=100),
                            showlegend=False,
                            xaxis_tickangle=-45
                        )
                    ),
                    html.Div([
                        html.P([
                            "Total Processed Transactions: ",
                            html.Span(
                                f"{client_data['Transactions'].sum():,}",
                                className="text-success"
                            )
                        ], className="mb-0 mt-3 regular-text text-center")
                    ])
                ])
            ], className="shadow-sm")
        ], width=6)
    ], className="mb-4")

], fluid=True, className="p-4")

# Initialize server for deployment
server = app.server

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run_server(debug=False, host='0.0.0.0', port=port)
