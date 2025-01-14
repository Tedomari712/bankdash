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

# Client logos mapping (Only significant volume clients)
CLIENT_LOGOS = {
    'Lemfi': 'assets/LEMFI.png',
    'DLocal': 'assets/DLocal.png',
    'Nala': 'assets/Nala.png',
    'Wapipay': 'assets/wapipay.jpg'
}

# Monthly data (filtered for active periods)
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

# Client data (filtered for active clients)
client_data = pd.DataFrame({
    'Client': ['Lemfi', 'DLocal', 'Nala', 'Wapipay'],
    'Volume': [2686506229.61, 353927405.68, 23023985.63, 18400642.19],
    'Transactions': [38712, 3928, 286, 99],
    'Market_Share': [87.17, 11.48, 0.75, 0.60]
})

# Complete 24-hour data
hourly_data = pd.DataFrame({
    'Hour': [
        '12:00 AM', '12:30 AM', '1:00 AM', '1:30 AM', '2:00 AM', '2:30 AM',
        '3:00 AM', '3:30 AM', '4:00 AM', '4:30 AM', '5:00 AM', '5:30 AM',
        '6:00 AM', '6:30 AM', '7:00 AM', '7:30 AM', '8:00 AM', '8:30 AM',
        '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM',
        '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM',
        '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM', '8:00 PM', '8:30 PM',
        '9:00 PM', '9:30 PM', '10:00 PM', '10:30 PM', '11:00 PM', '11:30 PM'
    ],
    'Volume': [
        31422733.80, 34824950.20, 37178383.70, 39343104.80, 33641452.40, 32227031.80,
        34648925.80, 32454662.20, 42374824.70, 43128807.70, 46059732.10, 57139036.40,
        58015932.50, 62236995.30, 60833204.50, 55974572.20, 77837841.00, 67626737.50,
        84461058.30, 75435087.40, 67624749.70, 79260334.80, 76847398.60, 73021931.70,
        84368774.00, 76140912.70, 92760212.00, 105426317.00, 99512228.50, 105454542.00,
        98766290.10, 88942862.10, 90963921.30, 87242973.80, 82701870.30, 83827382.50,
        84363714.10, 76609016.90, 66024103.70, 69091915.10, 66969157.00, 57814906.70,
        51346076.60, 47763253.40, 52829165.80, 41435365.70, 33925854.50, 33958558.20
    ],
    'Count': [
        438, 449, 517, 510, 450, 418, 441, 469, 546, 574, 633, 774,
        820, 815, 843, 789, 1026, 980, 1131, 1095, 1020, 1120, 1067, 1045,
        1129, 1060, 1243, 1359, 1288, 1383, 1366, 1281, 1254, 1237, 1228, 1164,
        1172, 1093, 997, 990, 944, 887, 801, 753, 727, 644, 551, 509
    ]
})

# Begin layout
app.layout = dbc.Container([
    # Header with VNGRD Logo
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(
                    src='assets/vngrd.PNG',
                    style={
                        'height': '150px',
                        'objectFit': 'contain',
                        'marginBottom': '20px'
                    }
                ),
                html.H1(
                    "2024 Annual Bank Transfer Analysis", 
                    className="text-primary text-center",
                    style={
                        'letterSpacing': '2px',
                        'marginTop': '20px'
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
                        "81.87",
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

        # Total Unique Users Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Unique Users", className="card-title text-center"),
                    html.H2(
                        f"42,574", 
                        className="text-primary text-center"
                    ),
                    html.P([
                        html.Span("Monthly Growth Rate: ", className="regular-text"),
                        html.Span(
                            f"189.92%",
                            className="regular-text text-success"
                        )
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ])
    ], className="mb-4 g-3"),

    # Monthly Transaction Analysis
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Monthly Transaction Analysis"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                name='Transaction Volume',
                                x=monthly_data['Month'],
                                y=monthly_data['Volume']/1e6,
                                marker_color='rgba(26, 118, 255, 0.8)',
                                yaxis='y',
                                text=monthly_data['Volume'].apply(lambda x: f'KES {x/1e6:,.0f}M'),
                                textposition='inside',
                                hovertemplate=(
                                    "<b>%{x}</b><br>" +
                                    "Volume: KES %{y:,.0f}M<br>" +
                                    "<extra></extra>"
                                )
                            ),
                            go.Scatter(
                                name='Transaction Count',
                                x=monthly_data['Month'],
                                y=monthly_data['Transactions'],
                                mode='lines+markers+text',
                                marker=dict(
                                    size=8,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                line=dict(
                                    width=2,
                                    color='rgba(255, 128, 0, 0.8)'
                                ),
                                text=monthly_data['Transactions'].apply(lambda x: f'{x:,}'),
                                textposition='top center',
                                yaxis='y2',
                                hovertemplate=(
                                    "<b>%{x}</b><br>" +
                                    "Transactions: %{y:,.0f}<br>" +
                                    "<extra></extra>"
                                )
                            )
                        ]).update_layout(
                            title={
                                'text': 'Monthly Growth Trends (June - December)',
                                'y': 0.95
                            },
                            yaxis=dict(
                                title='Volume (KES Millions)',
                                titlefont=dict(color='rgba(26, 118, 255, 0.8)'),
                                tickfont=dict(color='rgba(26, 118, 255, 0.8)'),
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.1)'
                            ),
                            yaxis2=dict(
                                title='Number of Transactions',
                                titlefont=dict(color='rgba(255, 128, 0, 0.8)'),
                                tickfont=dict(color='rgba(255, 128, 0, 0.8)'),
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            height=400,
                            margin=dict(l=50, r=50, t=50, b=50),
                            legend=dict(
                                orientation="h",
                                y=1.1,
                                x=0.5,
                                xanchor='center'
                            ),
                            hovermode='x unified',
                            showlegend=True,
                            plot_bgcolor='white'
                        )
                    )
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="mb-4"),

    # Success Rate Gauge and User Activity Metrics
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
                                value=81.87,
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
                                    'bar': {'color': "#81C784"},
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
                    )
                ])
            ], className="shadow-sm")
        ], width=4),

        # User Activity Metrics
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("User Activity Metrics"),
                dbc.CardBody([
                    dcc.Graph(
                        figure=go.Figure(data=[
                            go.Scatter(
                                x=[0.2, 0.5, 0.8],
                                y=[1.15, 1.15, 1.15],
                                mode='text',
                                text=['🌍', '👥', '👤'],
                                textfont=dict(size=24),
                                hoverinfo='none',
                                showlegend=False
                            ),
                            go.Scatter(
                                x=[0.2, 0.5, 0.8],
                                y=[1, 1, 1],
                                mode='text',
                                text=['Active Countries', 'Total Remitters', 'Total Recipients'],
                                textfont=dict(size=14),
                                hoverinfo='none',
                                showlegend=False
                            ),
                            go.Scatter(
                                x=[0.2, 0.5, 0.8],
                                y=[0.85, 0.85, 0.85],
                                mode='text',
                                text=[
                                    f"16",  # Excluding 'Unknown'
                                    f"{monthly_data['Unique_Remitters'].sum():,}",
                                    f"{monthly_data['Unique_Recipients'].sum():,}"
                                ],
                                textfont=dict(size=24, color='#2E86C1'),
                                hoverinfo='none',
                                showlegend=False
                            )
                        ]).update_layout(
                            height=300,
                            showlegend=False,
                            xaxis=dict(
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                                range=[0, 1]
                            ),
                            yaxis=dict(
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                                range=[0.5, 1.2]
                            ),
                            margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white'
                        )
                    )
                ])
            ], className="shadow-sm")
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
                                labels=country_data[country_data['Country'] != 'Unknown']['Country'],
                                values=country_data[country_data['Country'] != 'Unknown']['Volume'],
                                textinfo='label+percent',
                                hole=0.3,
                                marker=dict(
                                    colors=[
                                        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'
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
                                ),
                                textfont=dict(size=12)
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
                            title={
                                'text': 'Hourly Volume and Transaction Count Distribution',
                                'y': 0.95
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
                                tickvals=list(range(len(hourly_data))),
                                dtick=2  # Show every second hour for better readability
                            ),
                            hovermode='x unified'
                        )
                    ),
                    html.Div([
                        html.P([
                            "Peak Volume Hour: ",
                            html.Span(
                                "1:30 PM",
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
                    # Client Logos Section
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
                                name='Transactions Count',
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
                                tickfont=dict(color='rgba(26, 118, 255, 0.8)'),
                                type='log',
                                exponentformat='none',
                                tickformat='.2f'
                            ),
                            yaxis2=dict(
                                title='Number of Transactions',
                                titlefont=dict(color='rgba(255, 128, 0, 0.8)'),
                                tickfont=dict(color='rgba(255, 128, 0, 0.8)'),
                                overlaying='y',
                                side='right',
                                type='log',
                                exponentformat='none'
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
