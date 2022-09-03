from finModel.viz.generic import graph_settings, ChartLabels, set_labels_format, Colors
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from typing import Tuple, List
import seaborn as sns
import pandas as pd


def plot_ebitda_revenue_ratio(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(15,6)):
    fig,ax = plt.subplots(1,2,figsize=size)
    # assign labels to be used
    left_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="Revenues",ylab="USD in thousands",y_fmt='{x:,.0f}',
                                        grp="type",ttl="A: Revenues from sales and services")
    right_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="EBITDA%",ylab="% of revenues",y_fmt='{x:.2%}',
                                         grp="type",ttl="B: EBITDA (%)")
    # create basic plots
    sns.barplot(data=data,x=left_lbl.x,y=left_lbl.y,hue=left_lbl.grp,dodge=False,ax=ax[0])
    sns.lineplot(data=data,x=right_lbl.x,y=right_lbl.y,hue=right_lbl.grp,ax=ax[1])
    sns.scatterplot(data=data,x=right_lbl.x,y=right_lbl.y,color="gray",ax=ax[1])
    # format the axis-ticks
    ax[0].yaxis.set_major_formatter(left_lbl.y_fmt)
    ax[1].yaxis.set_major_formatter(right_lbl.y_fmt)
    # set axis labels
    set_labels_format(ax[0],left_lbl)
    set_labels_format(ax[1],right_lbl)
    fig.suptitle(chart_ttl)
    graph_settings(ax)
    # add point labels
    for bar in ax[0].containers:
        ax[0].bar_label(bar,labels=[f'{x:,.0f}' for x in bar.datavalues])
    for i, txt in enumerate([f'{v:.2%}' for v in data[right_lbl.y]]):
        ax[1].annotate(txt,(data[right_lbl.x][i], data[right_lbl.y][i]))

def plot_unlevered_cashflows(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(10,6)):
    fig,ax = plt.subplots(1,1,figsize=size)
    lbl: ChartLabels = ChartLabels(x="year",xlab="",y="UFCF",ylab="USD in thousands",y_fmt='{x:,.0f}',grp="",ttl=chart_ttl)
    plt.stackplot(data[lbl.x].values,data["PV of UFCF"].values,
                  data["UFCF"].values-data["PV of UFCF"].values,
                  labels=["Present value of UFCF","UFCF"],
                  colors=Colors.values())
    plt.legend(loc='upper right')
    ax.yaxis.set_major_formatter(lbl.y_fmt)
    set_labels_format(ax,lbl)
    sns.set_theme(style="whitegrid")

def plot_ebitda_component(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(18,7)):
    fig,ax = plt.subplots(1,4,figsize=size)
    y_list: List[str] = ["Delta EBITDA","Delta revenues","Delta COGS","Delta OPEX"]
    lbl: List[ChartLabels] = [ChartLabels(x=y,xlab="",y="year",ylab="",grp="",ttl=y) for y in y_list]
    for i in range(0,len(lbl)):
        sns.barplot(data=data,x=lbl[i].x,y=lbl[i].y,dodge=False,ax=ax[i],color=list(Colors.values())[i])
        set_labels_format(ax[i],lbl[i])
        for bar in ax[i].containers:
            ax[i].bar_label(bar,labels=[f'{x:,.0f}' for x in bar.datavalues],label_type="center")
        ax[i].xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax[i].xaxis.tick_top()
    fig.suptitle(chart_ttl)
    graph_settings(ax,legend=False)

def plot_grouped_bars(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(15,4)):
    fig,ax1 = plt.subplots(1,1,figsize=size)
    lbl: ChartLabels = ChartLabels(x="year",xlab="",y="days",ylab="days",grp="metric",ttl=chart_ttl,y_fmt='{x:.0f}')
    sns.barplot(data=data,x=lbl.x,y=lbl.y,hue=lbl.grp,ax=ax1,color=list(Colors.keys())[:3])
    set_labels_format(ax1,lbl)
    ax1.yaxis.set_major_formatter(lbl.y_fmt)
    for bar in ax1.containers:
        ax1.bar_label(bar,labels=[f'{x:.0f}' for x in bar.datavalues])
    graph_settings(ax1,legend=False)
    ax1.legend().set_title("")

