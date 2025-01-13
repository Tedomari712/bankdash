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
            .client-logo {
                width: 60px;
                height: 30px;
                object-fit: contain;
                margin: 5px;
                padding: 5px;
                background-color: #ffffff;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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

# Client logos for significant volume clients (>1% market share)
CLIENT_LOGOS = {
    'Lemfi': 'assets/lemfi-logo.png',
    'DLocal': 'assets/dlocal-logo.png',
    'Nala': 'assets/nala-logo.png'
}

# Monthly data (filtered to remove months with zero activity)
monthly_data = pd.DataFrame({
    'Month': ['June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'Transactions': [3239, 6147, 7311, 5853, 9986, 11574, 8217],
    'Volume': [164960577.05, 344641363.80, 441605577.75, 333896656.06, 
               612844465.61, 660334518.30, 523575404.54],
    'Success_Rate': [76.97, 82.43, 85.21, 79.07, 84.20, 78.33, 86.84],
    'Unique_Remitters': [1179, 2337, 2845, 2422, 3561, 3784, 3367],
    'Unique_Recipients': [1669, 3076, 3265, 2704, 4139, 4366, 3858]
})

# Failure data
failure_data = pd.DataFrame({
    'Reason': ['Insufficient Balance', 'Timed Out', 'Invalid Account', 'Other',
               'General Failure', 'Invalid Details', 'Invalid Credit Party'],
    'Total': [4219, 1286, 1174, 1193, 754, 430, 223],
    'Percentage': [45.29, 13.80, 12.60, 12.81, 8.09, 4.62, 2.39]
})

# Country data (filtered to remove negligible volumes)
country_data = pd.DataFrame({
    'Country': ['USA', 'GBR', 'CAN', 'KEN', 'Unknown'],
    'Volume': [1348601980.70, 1263989309.40, 131969949.47, 109322547.12, 203331985.30],
    'Count': [15011, 20520, 2544, 1753, 2304],
    'Market_Share': [43.79, 41.04, 4.28, 3.55, 6.60]
})

# Client data (filtered to include only active clients)
client_data = pd.DataFrame({
    'Client': ['Lemfi', 'DLocal', 'Nala', 'Wapipay'],
    'Volume': [2686506229.61, 353927405.68, 23023985.63, 18400642.19],
    'Transactions': [38712, 3928, 286, 99],
    'Market_Share': [87.17, 11.48, 0.75, 0.60]
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

# Start App Layout
app.layout = dbc.Container([
    # Header with VNGRD Logo
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(
                    src='assets/vngrd.png',
                    style={
                        'height': '100px',
                        'objectFit': 'contain',
                        'marginBottom': '20px'
                    }
                ),
                html.H1(
                    "2024 ANNUAL BANK TRANSFER ANALYSIS", 
                    className="text-primary text-center",
                    style={
                        'letterSpacing': '2px',
                        'marginTop': '20px',
                        'fontWeight': 'bold'
                    }
                )
            ], className="text-center")
        ])
    ], className="mb-4"),

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
                        html.Span("Monthly Average: ", className="regular-text"),
                        html.Span(
                            f"{monthly_data['Transactions'].mean():,.0f}",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ]),
        
        # Success Rate Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Average Success Rate", className="card-title text-center"),
                    html.H2([
                        f"{monthly_data['Success_Rate'].mean():.1f}",
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
            ], className="shadow-sm h-100")
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
                            f"KES {monthly_data['Volume'].mean()/1e6:,.0f}M",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ]),

        # User Activity Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("User Activity Metrics", className="card-title text-center"),
                    html.Div([
                        html.P([
                            html.I(className="fas fa-users me-2"),
                            "Total Remitters: ",
                            html.Span(
                                f"{monthly_data['Unique_Remitters'].sum():,.0f}",
                                className="text-primary"
                            )
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-user-check me-2"),
                            "Total Recipients: ",
                            html.Span(
                                f"{monthly_data['Unique_Recipients'].sum():,.0f}",
                                className="text-success"
                            )
                        ], className="mb-0")
                    ], className="text-center regular-text")
                ])
            ], className="shadow-sm h-100")
        ])
    ], className="mb-4 g-3"),

    # Monthly Trends Row
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
                                range=[75, 90]  # Adjusted to better show the variations
                            ),
                            height=400,
                            margin=dict(l=50, r=50, t=50, b=30),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            ),
                            hovermode='x unified'
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="mb-4")

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
                                value=81.87,  # Updated success rate
                                title={
                                    "text": "Average Success Rate",
                                    "font": {"size": 16, "color": "#2E7D32"}
                                },
                                number={
                                    "suffix": "%",
                                    "font": {"size": 28, "color": "#2E7D32"}
                                },
                                gauge={
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': "#81C784"},  # Light green
                                    'steps': [
                                        {'range': [0, 60], 'color': "rgba(129, 199, 132, 0.2)"},  
                                        {'range': [60, 75], 'color': "rgba(129, 199, 132, 0.4)"},
                                        {'range': [75, 90], 'color': "rgba(129, 199, 132, 0.6)"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "#4CAF50", 'width': 2},
                                        'thickness': 0.75,
                                        'value': 81.87
                                    }
                                }
                            )
                        ).update_layout(
                            height=300,
                            margin=dict(l=30, r=30, t=30, b=30)
                        )
                    ),
                    html.Div([
                        html.P([
                            "Peak Month: ",
                            html.Span(
                                f"December ({monthly_data['Success_Rate'].max():.1f}%)",
                                className="text-success"
                            )
                        ], className="mb-0 mt-3 regular-text text-center")
                    ])
                ])
            ], className="shadow-sm h-100")
        ], width=4),

        # User Activity Metrics
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("User Activity Metrics"),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure([
                                go.Indicator(
                                    mode="number",
                                    value=monthly_data['Unique_Remitters'].sum(),
                                    title={"text": "Total Remitters"},
                                    number={"font": {"size": 30}},
                                    domain={"row": 0, "column": 0}
                                ),
                                go.Indicator(
                                    mode="number",
                                    value=monthly_data['Unique_Recipients'].sum(),
                                    title={"text": "Total Recipients"},
                                    number={"font": {"size": 30}},
                                    domain={"row": 0, "column": 1}
                                ),
                                go.Indicator(
                                    mode="number",
                                    value=len(country_data) - 1,  # Excluding 'Unknown'
                                    title={"text": "Active Countries"},
                                    number={"font": {"size": 30}},
                                    domain={"row": 1, "column": 0}
                                ),
                                go.Indicator(
                                    mode="number",
                                    value=monthly_data['Transactions'].mean(),
                                    title={"text": "Avg Monthly Transactions"},
                                    number={
                                        "font": {"size": 30},
                                        "valueformat": ",.0f"
                                    },
                                    domain={"row": 1, "column": 1}
                                )
                            ]).update_layout(
                                grid={"rows": 2, "columns": 2, "pattern": "independent"},
                                height=300,
                                margin=dict(l=30, r=30, t=30, b=30)
                            )
                        )
                    ])
                ])
            ], className="shadow-sm h-100")
        ], width=8)
    ], className="mb-4"),

    # Geographic Distribution and Failure Analysis
    dbc.Row([
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
                                marker=dict(
                                    colors=[
                                        '#1f77b4', '#ff7f0e', '#2ca02c', 
                                        '#d62728', '#9467bd'
                                    ]
                                ),
                                hovertemplate=(
                                    "<b>%{label}</b><br>" +
                                    "Volume: KES %{value:,.2f}<br>" +
                                    "Share: %{percent}<br>" +
                                    "<extra></extra>"
                                )
                            )
                        ).update_layout(
                            title={
                                'text': 'Transaction Volume by Country',
                                'y': 0.95
                            },
                            height=400,
                            margin=dict(l=20, r=120, t=40, b=20),
                            showlegend=True,
                            legend=dict(
                                yanchor="middle",
                                y=0.5,
                                xanchor="right",
                                x=1.1,
                                bgcolor='rgba(255, 255, 255, 0.8)',
                                bordercolor='rgba(0, 0, 0, 0.1)',
                                borderwidth=1
                            ),
                            annotations=[{
                                'text': f'Total Volume:<br>KES {country_data["Volume"].sum()/1e9:.2f}B',
                                'x': 0.5,
                                'y': 0.5,
                                'font': {'size': 12},
                                'showarrow': False
                            }]
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=6),

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
                                    "Percentage: %{percentParent:.1%}<br>" +
                                    "<extra></extra>"
                                ),
                                marker=dict(
                                    colors=failure_data['Total'],
                                    colorscale='Reds',
                                    showscale=True
                                )
                            )
                        ).update_layout(
                            title={
                                'text': 'Transaction Failure Distribution',
                                'y': 0.95
                            },
                            height=400,
                            margin=dict(l=20, r=20, t=40, b=20)
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
        ], width=6)
    ], className="mb-4")

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
                            title={
                                'text': 'Hourly Volume and Transaction Count Distribution',
                                'y': 0.95,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top'
                            },
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
                            height=400,
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
                            ),
                            hovermode='x unified'
                        )
                    ),
                    html.Div([
                        html.P([
                            "Peak Activity: ",
                            html.Span(
                                "9:00:00 AM",
                                className="text-success"
                            ),
                            html.Span(
                                f" ({hourly_data['Count'].max():,} transactions, KES {hourly_data['Volume'].max()/1e6:.1f}M)",
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
                                        '#526DFF', '#FF6347', '#20B2AA', '#FF9F40'
                                    ]
                                ),
                                hovertemplate=(
                                    "<b>%{label}</b><br>" +
                                    "Market Share: %{value:.1f}%<br>" +
                                    "<extra></extra>"
                                )
                            )]
                        ).update_layout(
                            title={
                                'text': 'Market Share Distribution',
                                'y': 0.95
                            },
                            height=400,
                            margin=dict(l=20, r=120, t=40, b=20),
                            showlegend=True,
                            legend=dict(
                                yanchor="middle",
                                y=0.5,
                                xanchor="right",
                                x=1.1,
                                bgcolor='rgba(255, 255, 255, 0.8)',
                                bordercolor='rgba(0, 0, 0, 0.1)',
                                borderwidth=1
                            )
                        )
                    ),
                    # Client Logos
                    html.Div([
                        html.Div([
                            html.Img(
                                src=logo_path,
                                className='client-logo',
                                title=client
                            ) for client, logo_path in CLIENT_LOGOS.items()
                        ], style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'flexWrap': 'wrap',
                            'gap': '10px',
                            'marginTop': '20px'
                        })
                    ])
                ])
            ], className="shadow-sm")
        ], width=6),

        # Client Performance
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Client Performance Analysis"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                name='Transaction Volume',
                                x=client_data['Client'],
                                y=client_data['Volume']/1e9,
                                marker_color='rgba(26, 118, 255, 0.8)',
                                hovertemplate=(
                                    "<b>%{x}</b><br>" +
                                    "Volume: KES %{y:.2f}B<br>" +
                                    "<extra></extra>"
                                )
                            ),
                            go.Scatter(
                                name='Transactions',
                                x=client_data['Client'],
                                y=client_data['Transactions'],
                                mode='lines+markers',
                                marker=dict(size=8),
                                yaxis='y2',
                                hovertemplate=(
                                    "<b>%{x}</b><br>" +
                                    "Transactions: %{y:,.0f}<br>" +
                                    "<extra></extra>"
                                )
                            )
                        ]).update_layout(
                            title='Client Performance Metrics',
                            yaxis=dict(
                                title='Volume (KES Billions)',
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
                            margin=dict(l=50, r=50, t=50, b=100),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            ),
                            xaxis_tickangle=-45,
                            hovermode='x unified'
                        )
                    ),
                    html.Div([
                        html.P([
                            "Leading Client: ",
                            html.Span(
                                f"{client_data.iloc[0]['Client']} ",
                                className="text-success"
                            ),
                            html.Span(
                                f"(KES {client_data.iloc[0]['Volume']/1e9:.2f}B, {client_data.iloc[0]['Transactions']:,} transactions)",
                                className="text-muted"
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
