# -*- coding: utf-8 -*-
"""Dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1i_HpBPRtNsnbNf9AVN2RCv2pXIDUIKDW
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# Load datasets
stock_predictions = pd.read_csv("stock_price_predictions_with_close_5.csv")
all_predictions = pd.read_csv("all_predictions_24_11_.csv")
technicals_data = pd.read_csv("dashboard_technical_indicators_dataset.csv")
earnings_data = pd.read_csv("dashboard_dataset.csv")

all_predictions['predictions'] = all_predictions['predictions'].apply(lambda x: round(x*100, 2))
all_predictions.head()

# Initialize Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Stock Dashboard"
# Expose the Flask server to be used with Gunicorn
server = app.server

# Calculate Top 5 Best and Worst Predictions
top5_best = all_predictions.nlargest(5, 'predictions')
top5_worst = all_predictions.nsmallest(5, 'predictions')

# Layout
app.layout = dbc.Container(
    [
        # Top row: Top 5 Best and Worst Predictions
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Top 5 Best Predictions", className="text-center"),
                        dcc.Graph(id="best-bar-chart", config={"displayModeBar": False}),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H5("Top 5 Worst Predictions", className="text-center"),
                        dcc.Graph(id="worst-bar-chart", config={"displayModeBar": False}),
                    ],
                    width=6,
                ),
            ],
            className="mb-4",
        ),

        # Second row: Dropdown and dynamic text for predicted return
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Ticker:", style={"font-size": "20px", "font-weight": "bold"}),
                        dcc.Dropdown(
                            id="ticker-dropdown",
                            options=[{"label": ticker, "value": ticker} for ticker in all_predictions["ticker"].unique()],
                            value=all_predictions["ticker"].iloc[0],
                            clearable=False,
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        id="predicted-return-text",
                        className="text-center",
                        style={"font-weight": "bold", "color": "#333"},
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),

        # Third row: Revenue and EPS charts side by side
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Revenue Chart", className="text-center"),
                        dcc.Graph(id="revenue-chart", config={"displayModeBar": False}),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H5("EPS Chart", className="text-center"),
                        dcc.Graph(id="eps-chart", config={"displayModeBar": False}),
                    ],
                    width=6,
                ),
            ],
            className="mb-4",
        ),

        # Fourth row: Price chart with SMA toggle and RSI
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Price Chart with Predicted Value", className="text-center"),
                        dcc.Graph(id="price-chart", config={"displayModeBar": False}),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button("Include SMA", id="sma-button", color="primary", className="m-2", n_clicks=0),
                                ),
                                dbc.Col(
                                    dbc.Button("Exclude SMA", id="exclude-sma-button", color="secondary", className="m-2", n_clicks=0),
                                ),
                            ],
                            justify="center",
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        html.H5("RSI Chart", className="text-center"),
                        dcc.Graph(id="rsi-chart", config={"displayModeBar": False}),
                    ],
                    width=4,
                ),
            ],
            className="mb-4",
        ),

        # Footer
        dbc.Row(
            [
                dbc.Col(
                    html.Footer("Powered by Timur Mamadaliyev", className="text-center mt-4"),
                    width=12,
                ),
            ],
        ),
    ],
    fluid=True,
)

# Update the dynamic predicted return text
@app.callback(
    Output("predicted-return-text", "children"),
    Input("ticker-dropdown", "value"),
)
def update_predicted_return_text(ticker):
    predicted_return = all_predictions[all_predictions["ticker"] == ticker]["predictions"].iloc[0]
    return f"The predicted return of the {ticker} is {predicted_return:.2f}%."


# Update all dashboard figures dynamically
@app.callback(
    [
        Output("best-bar-chart", "figure"),
        Output("worst-bar-chart", "figure"),
        Output("revenue-chart", "figure"),
        Output("eps-chart", "figure"),
        Output("price-chart", "figure"),
        Output("rsi-chart", "figure"),
    ],
    [
        Input("ticker-dropdown", "value"),
        Input("sma-button", "n_clicks"),
        Input("exclude-sma-button", "n_clicks"),
     ],
)
def update_dashboard(ticker, include_sma_clicks, exclude_sma_clicks):
    # Top 5 Best and Worst Bar Charts
    best_fig = go.Figure()
    best_fig.add_trace(go.Bar(x=top5_best["ticker"], y=top5_best["predictions"], marker_color="green"))
    best_fig.update_layout(title="Top 5 Best Predictions", yaxis_title="Predictions (%)")

    worst_fig = go.Figure()
    worst_fig.add_trace(go.Bar(x=top5_worst["ticker"], y=top5_worst["predictions"], marker_color="red"))
    worst_fig.update_layout(title="Top 5 Worst Predictions", yaxis_title="Predictions (%)")

    # Filter data for selected ticker
    ticker_data = stock_predictions[stock_predictions["ticker"] == ticker]
    ticker_technicals = technicals_data[(technicals_data["ticker"] == ticker) & (technicals_data["date"] >= "2023-01-01")]
    ticker_earnings = earnings_data[earnings_data["ticker"] == ticker]

    # Price Chart with Confidence Interval
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=ticker_data["ds"], y=ticker_data["y"], mode="lines", name="Close Price"))
    price_fig.add_trace(go.Scatter(x=ticker_data["ds"], y=ticker_data["yhat"], mode="lines", line_color="orange", name="Forecast"))
    price_fig.add_trace(go.Scatter(x=ticker_data["ds"], y=ticker_data["yhat_lower"], mode="lines", line_color="lightblue", name="Lower Bound"))
    price_fig.add_trace(go.Scatter(x=ticker_data["ds"], y=ticker_data["yhat_upper"], mode="lines", fill="tonexty", line_color="lightblue", name="Upper Bound"))
    if include_sma_clicks > exclude_sma_clicks:
        price_fig.add_trace(go.Scatter(x=ticker_technicals["date"], y=ticker_technicals["sma"], mode="lines", name="SMA"))
    price_fig.update_layout(title=f"Price Chart for {ticker}", xaxis_title="Date", yaxis_title="Price")

    # RSI Chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=ticker_technicals["date"], y=ticker_technicals["rsi"], mode="lines", name="RSI"))
    rsi_fig.add_shape(type="rect", x0=ticker_technicals["date"].min(), x1=ticker_technicals["date"].max(),
                      y0=30, y1=70, fillcolor="lightgrey", opacity=0.2, layer="below")
    rsi_fig.update_layout(title=f"RSI for {ticker}", xaxis_title="Date", yaxis_title="RSI Value", yaxis=dict(range=[0, 100]))

    # Revenue Chart
    revenue_fig = go.Figure()
    revenue_fig.add_trace(go.Bar(x=ticker_earnings["date"], y=ticker_earnings["Revenue"], name="Revenue", marker_color="orange"))
    revenue_fig.update_layout(title=f"Revenue for {ticker}", xaxis_title="Quarter", yaxis_title="Revenue")

    # EPS Chart with Conditional Coloring
    eps_fig = go.Figure()
    eps_fig.add_trace(go.Bar(
        x=ticker_earnings["date"],
        y=ticker_earnings["EPS_Actual"],
        name="EPS Actual",
        marker_color=["red" if actual <= est else "green" for actual, est in zip(ticker_earnings["EPS_Actual"], ticker_earnings["EPS_Estimate"])],
    ))
    eps_fig.add_trace(go.Scatter(x=ticker_earnings["date"], y=ticker_earnings["EPS_Estimate"], mode="lines+markers", name="EPS Estimate", marker_color="yellow"))
    eps_fig.update_layout(
        title=f"EPS for {ticker}",
        xaxis_title="Quarter",
        yaxis=dict(title="EPS Values"),
        barmode="group",
    )

    return best_fig, worst_fig, revenue_fig, eps_fig, price_fig, rsi_fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=False, use_reloader=False)
