"""
Chart components for the Project Risk Management System.
These components generate various visualizations for the Streamlit frontend.
"""
import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

from backend.data.models import Project, Risk, RiskSeverity, RiskCategory, RiskStatus


def create_risk_heatmap(risks: list[Risk]) -> go.Figure:
    """
    Create a risk heatmap based on probability and severity.
    
    Args:
        risks: List of Risk objects
        
    Returns:
        Plotly figure object with the risk heatmap
    """
    # Map severity and probability to numeric values
    severity_map = {
        RiskSeverity.LOW: 1,
        RiskSeverity.MEDIUM: 2, 
        RiskSeverity.HIGH: 3,
        RiskSeverity.CRITICAL: 4
    }
    
    probability_map = {
        "unlikely": 1,
        "possible": 2,
        "likely": 3,
        "very_likely": 4
    }
    
    # Create data for heatmap
    risk_data = []
    for risk in risks:
        risk_data.append({
            'id': risk.id,
            'title': risk.title,
            'severity_value': severity_map[risk.severity],
            'severity': risk.severity.value.capitalize(),
            'probability_value': probability_map[risk.probability],
            'probability': risk.probability.value.replace('_', ' ').capitalize(),
            'score': risk.risk_score,
            'category': risk.category.value.capitalize(),
            'status': risk.status.value.capitalize()
        })
    
    if not risk_data:
        # Create empty figure if no risks
        fig = go.Figure()
        fig.update_layout(
            title="Risk Heatmap (No Risks Available)",
            xaxis_title="Severity",
            yaxis_title="Probability",
            height=500
        )
        return fig
    
    # Convert to DataFrame
    df = pd.DataFrame(risk_data)
    
    # Create bubble sizes based on number of risks at each point
    size_df = df.groupby(['severity_value', 'probability_value']).size().reset_index(name='count')
    
    # Create hover text
    hover_texts = []
    for _, row in size_df.iterrows():
        sev_val = row['severity_value']
        prob_val = row['probability_value']
        risks_at_point = df[(df['severity_value'] == sev_val) & (df['probability_value'] == prob_val)]
        
        text = f"Severity: {risks_at_point.iloc[0]['severity']}<br>"
        text += f"Probability: {risks_at_point.iloc[0]['probability']}<br>"
        text += f"Count: {len(risks_at_point)}<br>"
        text += "Risks:<br>"
        for _, risk in risks_at_point.iterrows():
            text += f"- {risk['title']} ({risk['category']})<br>"
        
        hover_texts.append(text)
    
    # Create colorscale
    colorscale = [
        [0, 'green'],      # Low risk
        [0.25, 'yellow'],  # Medium risk
        [0.5, 'orange'],   # High risk
        [0.75, 'red'],     # Critical risk
        [1, 'darkred']     # Extreme risk
    ]
    
    # Create heatmap with bubbles
    fig = go.Figure()
    
    # Add background colors
    severity_labels = ['Low', 'Medium', 'High', 'Critical']
    probability_labels = ['Unlikely', 'Possible', 'Likely', 'Very Likely']
    
    # Create heat map array
    heat_values = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            heat_values[i, j] = (i + 1) * (j + 1)  # Severity * Probability
    
    fig.add_trace(go.Heatmap(
        z=heat_values,
        x=severity_labels,
        y=probability_labels,
        colorscale=colorscale,
        showscale=True,
        colorbar=dict(title="Risk Score"),
    ))
    
    # Add bubbles representing risk counts
    fig.add_trace(go.Scatter(
        x=[severity_labels[i-1] for i in size_df['severity_value']],
        y=[probability_labels[i-1] for i in size_df['probability_value']],
        mode='markers',
        marker=dict(
            size=size_df['count'] * 10,  # Scale bubble size
            color='rgba(255, 255, 255, 0.8)',
            line=dict(width=2, color='black')
        ),
        text=hover_texts,
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title="Risk Heatmap",
        xaxis_title="Severity",
        yaxis_title="Probability",
        height=500
    )
    
    return fig


def create_project_health_timeline(project: Project) -> go.Figure:
    """
    Create a timeline of project health scores.
    
    Args:
        project: Project object with historical health scores
        
    Returns:
        Plotly figure object with the health timeline
    """
    # Extract historical health scores
    if not project.historical_health_scores:
        # Create sample data if no historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='W')
        
        # Create sample health scores with some variation
        health_scores = [project.health_score]
        for _ in range(1, len(dates)):
            # Add some random variation but keep within bounds
            change = np.random.uniform(-0.5, 0.5)
            new_score = max(0, min(10, health_scores[-1] + change))
            health_scores.append(new_score)
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'health_score': health_scores
        })
    else:
        # Use actual historical data
        df = pd.DataFrame(project.historical_health_scores)
    
    # Create figure
    fig = go.Figure()
    
    # Add line chart
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['score'] if 'score' in df.columns else df['health_score'],
        mode='lines+markers',
        line=dict(width=2, color='blue'),
        marker=dict(size=8, color='blue')
    ))
    
    # Add threshold zones
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="y",
        x0=0,
        y0=0,
        x1=1,
        y1=3,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
    )
    
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="y",
        x0=0,
        y0=3,
        x1=1,
        y1=6,
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0,
    )
    
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="y",
        x0=0,
        y0=6,
        x1=1,
        y1=10,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0,
    )
    
    fig.update_layout(
        title=f"Project Health Timeline: {project.name}",
        xaxis_title="Date",
        yaxis_title="Health Score",
        yaxis=dict(range=[0, 10]),
        height=400
    )
    
    return fig


def create_risk_category_distribution(risks: list[Risk]) -> go.Figure:
    """
    Create a pie chart showing distribution of risks by category.
    
    Args:
        risks: List of Risk objects
        
    Returns:
        Plotly figure object with the risk category distribution
    """
    # Count risks by category
    category_counts = {}
    for risk in risks:
        category = risk.category.value.capitalize()
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    # Create data for pie chart
    labels = list(category_counts.keys())
    values = list(category_counts.values())
    
    # Create color map
    colors = {
        'Financial': 'royalblue',
        'Technical': 'darkblue',
        'Schedule': 'orange',
        'Resource': 'green',
        'Market': 'purple',
        'Operational': 'red',
        'Strategic': 'teal',
        'Legal': 'darkred'
    }
    
    # Get colors for each category
    color_values = [colors.get(label, 'gray') for label in labels]
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=color_values
    )])
    
    fig.update_layout(
        title="Risk Distribution by Category",
        height=400
    )
    
    return fig


def create_risk_severity_gauge(risks: list[Risk]) -> go.Figure:
    """
    Create a gauge chart showing overall risk severity.
    
    Args:
        risks: List of Risk objects
        
    Returns:
        Plotly figure object with the risk severity gauge
    """
    if not risks:
        # Default to 0 if no risks
        overall_score = 0
    else:
        # Calculate overall risk score
        severity_scores = {
            RiskSeverity.LOW: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.HIGH: 3,
            RiskSeverity.CRITICAL: 4
        }
        
        total_score = sum(severity_scores[risk.severity] for risk in risks)
        total_possible = len(risks) * 4  # Maximum possible score
        
        overall_score = (total_score / total_possible) * 100 if total_possible > 0 else 0
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Risk Severity"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgray"},
            'steps': [
                {'range': [0, 25], 'color': "green"},
                {'range': [25, 50], 'color': "yellow"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': overall_score
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig


def create_risk_trend_chart(risks: list[Risk]) -> go.Figure:
    """
    Create a line chart showing risk score trends over time.
    
    Args:
        risks: List of Risk objects with historical scores
        
    Returns:
        Plotly figure object with the risk trend chart
    """
    # Select risks with historical data
    risks_with_history = [risk for risk in risks if risk.historical_scores]
    
    if not risks_with_history:
        # Create empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="Risk Score Trends (No Historical Data Available)",
            xaxis_title="Date",
            yaxis_title="Risk Score",
            height=400
        )
        return fig
    
    # Create figure
    fig = go.Figure()
    
    # Add line for each risk
    for risk in risks_with_history[:5]:  # Limit to 5 risks for clarity
        # Extract dates and scores
        dates = [item['date'] for item in risk.historical_scores]
        scores = [item['score'] for item in risk.historical_scores]
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name=risk.title[:30] + "..." if len(risk.title) > 30 else risk.title
        ))
    
    fig.update_layout(
        title="Risk Score Trends (Top 5 Risks)",
        xaxis_title="Date",
        yaxis_title="Risk Score",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_project_health_comparison(projects: list[Project]) -> go.Figure:
    """
    Create a bar chart comparing health scores across projects.
    
    Args:
        projects: List of Project objects
        
    Returns:
        Plotly figure object with the project health comparison
    """
    # Extract project names and health scores
    names = [project.name for project in projects]
    health_scores = [project.health_score for project in projects]
    
    # Create color scale based on health scores
    colors = []
    for score in health_scores:
        if score >= 7:
            colors.append('green')
        elif score >= 4:
            colors.append('orange')
        else:
            colors.append('red')
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=names,
        y=health_scores,
        marker_color=colors
    )])
    
    fig.update_layout(
        title="Project Health Comparison",
        xaxis_title="Project",
        yaxis_title="Health Score",
        yaxis=dict(range=[0, 10]),
        height=400
    )
    
    return fig


def create_risk_count_by_status(risks: list[Risk]) -> go.Figure:
    """
    Create a bar chart showing risk counts by status.
    
    Args:
        risks: List of Risk objects
        
    Returns:
        Plotly figure object with the risk status distribution
    """
    # Count risks by status
    status_counts = {}
    for risk in risks:
        status = risk.status.value.capitalize()
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    # Create data for bar chart
    statuses = list(status_counts.keys())
    counts = list(status_counts.values())
    
    # Create color map
    colors = {
        'Identified': 'red',
        'Assessed': 'orange',
        'Mitigating': 'blue',
        'Resolved': 'green',
        'Accepted': 'purple'
    }
    
    # Get colors for each status
    color_values = [colors.get(status, 'gray') for status in statuses]
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=statuses,
        y=counts,
        marker_color=color_values
    )])
    
    fig.update_layout(
        title="Risk Distribution by Status",
        xaxis_title="Status",
        yaxis_title="Number of Risks",
        height=400
    )
    
    return fig


def create_budget_vs_timeline_chart(project: Project) -> go.Figure:
    """
    Create a chart showing budget utilization vs timeline progress.
    
    Args:
        project: Project object
        
    Returns:
        Plotly figure object with the budget vs timeline chart
    """
    # Calculate budget utilization
    budget_used_percent = (project.expenditure_to_date / project.budget) * 100 if project.budget > 0 else 0
    
    # Calculate timeline progress
    if project.expected_end_date:
        total_days = (project.expected_end_date - project.start_date).days
        days_elapsed = (datetime.now() - project.start_date).days
        timeline_progress = (days_elapsed / total_days) * 100 if total_days > 0 else 0
    else:
        timeline_progress = 0
    
    # Create data for chart
    labels = ['Budget Utilization', 'Timeline Progress']
    values = [budget_used_percent, timeline_progress]
    
    # Create colors based on comparison
    budget_color = 'red' if budget_used_percent > timeline_progress + 10 else 'green'
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=[budget_color, 'blue'],
        text=[f"{budget_used_percent:.1f}%", f"{timeline_progress:.1f}%"],
        textposition='auto'
    )])
    
    # Add 45 degree line (ideal progress)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=0,
        x1=1.5,
        y1=100,
        line=dict(color="black", width=2, dash="dash"),
    )
    
    fig.update_layout(
        title=f"Budget vs Timeline Progress: {project.name}",
        yaxis_title="Percentage (%)",
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    return fig


def create_bubble_chart_risk_metrics(risks: list[Risk]) -> st.delta_generator.DeltaGenerator:
    """
    Create an interactive bubble chart of risks with multiple dimensions.
    
    Args:
        risks: List of Risk objects
        
    Returns:
        Altair chart object
    """
    # Create data for chart
    data = []
    for risk in risks:
        data.append({
            'id': risk.id,
            'title': risk.title[:30] + "..." if len(risk.title) > 30 else risk.title,
            'severity': risk.severity.value.capitalize(),
            'probability': risk.probability.value.replace('_', ' ').capitalize(),
            'category': risk.category.value.capitalize(),
            'status': risk.status.value.capitalize(),
            'score': risk.risk_score,
            'identified_date': risk.identified_date,
            'days_since_identification': (datetime.now() - risk.identified_date).days
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        return st.error("No risk data available for visualization.")
    
    # Create Altair chart
    chart = alt.Chart(df).mark_circle().encode(
        x=alt.X('days_since_identification:Q', title='Days Since Identification'),
        y=alt.Y('score:Q', title='Risk Score'),
        size=alt.Size('score:Q', scale=alt.Scale(range=[100, 1000]), title='Risk Score'),
        color=alt.Color('category:N', title='Category'),
        tooltip=['title', 'severity', 'probability', 'category', 'status', 'score', 'days_since_identification']
    ).properties(
        width=700,
        height=400,
        title='Risk Bubble Chart'
    ).interactive()
    
    return st.altair_chart(chart)