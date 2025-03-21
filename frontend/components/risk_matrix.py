# risk_matrix.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def display_risk_matrix(risk_df):
    """
    Display a 5x5 risk matrix visualization
    
    Args:
        risk_df (pd.DataFrame): DataFrame containing risk data with probability and impact columns
    """
    # If the DataFrame is empty or doesn't have required columns, show placeholder
    if risk_df.empty or 'probability' not in risk_df.columns or 'impact' not in risk_df.columns:
        st.warning("Not enough risk data to display the risk matrix.")
        return
    
    # Create a 5x5 grid for the risk matrix
    matrix = np.zeros((5, 5))
    
    # Map risk severity to colors
    colors = {'high': 'red', 'medium': 'orange', 'low': 'green'}
    
    # Prepare data for the matrix
    x = []  # Impact
    y = []  # Probability
    text = []  # Risk names for hover
    color = []  # Colors based on severity
    
    # Process each risk
    for _, risk in risk_df.iterrows():
        # Adjust for 0-based indexing
        prob = int(risk['probability']) - 1 if 'probability' in risk else 0
        impact = int(risk['impact']) - 1 if 'impact' in risk else 0
        
        prob = max(0, min(prob, 4))  # Ensure within 0-4 range
        impact = max(0, min(impact, 4))  # Ensure within 0-4 range
        
        x.append(impact)
        y.append(prob)
        
        # Risk name or ID for hover text
        risk_name = risk.get('name', f"Risk {risk.get('id', 'unknown')}")
        text.append(risk_name)
        
        # Color based on severity
        risk_color = colors.get(risk.get('severity', 'low'), 'green')
        color.append(risk_color)
    
    # Create the figure
    fig = go.Figure()
    
    # Add scatter plot for risks
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=15,
            color=color,
            line=dict(width=1, color='black')
        ),
        text=text,
        hoverinfo='text'
    ))
    
    # Create background color zones for the matrix
    # High risk zone (red)
    fig.add_shape(
        type="rect",
        x0=2.5, y0=2.5, x1=5, y1=5,
        line=dict(width=0),
        fillcolor="rgba(255, 0, 0, 0.2)"
    )
    
    # Medium risk zone (orange)
    fig.add_shape(
        type="rect",
        x0=1.5, y0=1.5, x1=5, y1=5,
        line=dict(width=0),
        fillcolor="rgba(255, 165, 0, 0.2)",
        layer="below"
    )
    
    # Low risk zone (green)
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=5, y1=5,
        line=dict(width=0),
        fillcolor="rgba(0, 128, 0, 0.2)",
        layer="below"
    )
    
    # Configure the layout
    fig.update_layout(
        title="Risk Matrix",
        xaxis=dict(
            title="Impact",
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['1', '2', '3', '4', '5'],
            range=[-0.5, 4.5]
        ),
        yaxis=dict(
            title="Probability",
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['1', '2', '3', '4', '5'],
            range=[-0.5, 4.5]
        ),
        height=500,
        showlegend=False
    )
    
    # Add grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)