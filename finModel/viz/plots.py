from finModel.viz.generic import ChartLabels, Colors
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import Tuple, List
import pandas as pd
import numpy as np


def plot_ebitda_revenue_ratio(data:pd.DataFrame,chart_ttl:str) -> go.Figure:
    # assign labels to be used
    l_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="Revenues",ylab="USD in thousands",
                                     grp="type",ttl="A: Revenues from sales and services")
    r_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="EBITDA%",ylab="% of revenues",
                                     grp="type",ttl="B: EBITDA (%)")
    # create basic plots
    fig = make_subplots(rows=1,cols=2,subplot_titles=(l_lbl.ttl,r_lbl.ttl))
    fig.add_trace(go.Bar(x=data[l_lbl.x],y=data[l_lbl.y],hovertemplate='%{y:,.0f}<br>%{x}',name=l_lbl.y,
                         marker={'color':Colors['cobalt blue']}),row=1,col=1)
    fig.add_trace(go.Scatter(x=data[r_lbl.x],y=data[r_lbl.y],hovertemplate='%{y:.2%}<br>%{x}',name=r_lbl.y,
                             marker={'color':Colors['cobalt blue']}),row=1,col=2)

    fig.update_yaxes(row=1,col=1,title_text=l_lbl.ylab,tickformat=',.0f')
    fig.update_yaxes(row=1,col=2,title_text=r_lbl.ylab,tickformat='.2%')

    fig.update_layout(height=500,width=1100,title=chart_ttl,template='simple_white',plot_bgcolor='#F9F9FA')

    return fig


def plot_unlevered_cashflows(data:pd.DataFrame,chart_ttl:str) -> go.Figure:
    lbl: ChartLabels = ChartLabels(x="year",xlab="",y="UFCF",y2="PV of UFCF",ylab="USD in thousands")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data[lbl.x], y=data[lbl.y2], fill='tozeroy', mode='none',hovertemplate='%{y:,.0f}<br>%{x}',
                  name=lbl.y2,fillcolor=Colors['cobalt blue']))
    fig.add_trace(go.Scatter(x=data[lbl.x], y=data[lbl.y], fill='tonexty', mode='none',hovertemplate='%{y:,.0f}<br>%{x}',
                             name=lbl.y,fillcolor=Colors['light blue']))
    fig.update_yaxes(title_text=lbl.ylab,tickformat=',.0f')
    fig.update_layout(height=500,width=700,title=chart_ttl,template='simple_white',plot_bgcolor='#F9F9FA')

    return fig


def plot_ebitda_component(data:pd.DataFrame,chart_ttl:str) -> go.Figure:
    fig = go.Figure()
    y_list: List[str] = ["Delta revenues","Delta COGS","Delta OPEX"]
    lbl: List[ChartLabels] = [ChartLabels(x="year",xlab="",y=y,ylab="USD in thousands") for y in y_list]
    for i in range(0,len(lbl)):
        fig.add_trace(go.Bar(x=data[lbl[i].x],y=data[lbl[i].y],hovertemplate='%{y:,.0f}<br>%{x}',name=lbl[i].y,
                             marker={'color':list(Colors.values())[i]}, opacity=0.5))
    fig.update_layout(barmode='relative', height=500, width=1000, title=chart_ttl, template='simple_white',
                      plot_bgcolor='#F9F9FA')
    fig.add_trace(go.Scatter(x=data["year"],y=data["Delta EBITDA"],hovertemplate="%{y:,.0f}",name="Delta EBITDA",
                             marker={'color':'black'}))
    fig.update_yaxes(title_text=lbl[0].ylab,tickformat=',.0f')

    return fig


def plot_days_component(data:pd.DataFrame,chart_ttl:str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    y_list: List[str] = ["DSO","DIO","DPO"]
    lbl: List[ChartLabels] = [ChartLabels(x="year",xlab="",y=y,y2="Working capital",ylab="days",y2lab="USD in thousands") for y in y_list]
    for i in range(0,len(lbl)):
        fig.add_trace(go.Bar(x=data[lbl[i].x],y=data[lbl[i].y],hovertemplate='%{y:.0f}<br>%{x}',name=lbl[i].y,
                             marker={'color':list(Colors.values())[i]}, opacity=0.5))
    fig.update_layout(barmode='relative', height=500, width=1000, title=chart_ttl, template='simple_white',
                      plot_bgcolor='#F9F9FA')
    fig.add_trace(go.Scatter(x=data[lbl[0].x],y=data[lbl[0].y2],hovertemplate="%{y:,.0f}",name=lbl[0].y2,
                             marker={'color':'black'}),secondary_y=True)
    fig.update_yaxes(secondary_y=False,title_text=lbl[0].ylab,tickformat='.0f')
    fig.update_yaxes(secondary_y=True,title_text=lbl[0].y2lab,tickformat=',.0f')

    return fig


def plot_wc_component(data:pd.DataFrame,chart_ttl:str) -> go.Figure:
    fig = go.Figure()
    y_list: List[str] = ["Trade receivables","Inventory","Trade payables"]
    lbl: List[ChartLabels] = [ChartLabels(x="year",xlab="",y=y,y2="Working capital",ylab="USD in thousands") for y in y_list]
    for i in range(0,len(lbl)):
        fig.add_trace(go.Bar(x=data[lbl[i].x],y=data[lbl[i].y],hovertemplate='%{y:,.0f}<br>%{x}',name=lbl[i].y,
                             marker={'color':list(Colors.values())[i]}, opacity=0.5))
    fig.update_layout(barmode='relative', height=500, width=1000, title=chart_ttl, template='simple_white',
                      plot_bgcolor='#F9F9FA')
    fig.add_trace(go.Scatter(x=data[lbl[0].x],y=data[lbl[0].y2],hovertemplate="%{y:,.0f}",name=lbl[0].y2,
                             marker={'color':'black'}))
    fig.update_yaxes(title_text=lbl[0].ylab,tickformat=',.0f')

    return fig


def plot_enterprise_vals(data:pd.DataFrame,lbl:ChartLabels) -> go.Figure:
    x=np.array([f"Simulation {i+1}" for i in data.index])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=data[lbl.y], fill='tozeroy', mode='none',hovertemplate='%{y:,.0f}',
                             name=lbl.y,fillcolor=Colors['cobalt blue']))
    fig.add_trace(go.Scatter(x=x,y=data[lbl.x],hovertemplate='%{y:.2%}',name=lbl.x,mode="none"))
    fig.add_trace(go.Scatter(x=x,y=data[lbl.y2],hovertemplate='%{y:.2%}',name=lbl.y2,mode="none"))
    fig.update_yaxes(title_text=lbl.ylab,tickformat=',.0f')
    fig.update_xaxes(title_text="",visible=False)
    fig.update_layout(height=500,width=1000,title=lbl.ttl,template='simple_white',plot_bgcolor='#F9F9FA',
                      hovermode='x unified')
    return fig