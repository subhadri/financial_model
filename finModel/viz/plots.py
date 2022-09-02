from finModel.viz.generic import graph_settings, ChartLabels, set_labels_format
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from typing import Tuple
import seaborn as sns
import pandas as pd


def plot_ebitda_revenue_ratio(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(15,6)):
    fig,ax = plt.subplots(1,2,figsize=size)
    left_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="Revenues",ylab="USD in thousands",
                                        y_fmt=StrMethodFormatter('{x:,.0f}'),grp="type",
                                        ttl="A: Revenues from sales and services")
    right_lbl: ChartLabels = ChartLabels(x="year",xlab="",y="EBITDA%",ylab="% of revenues",
                                        y_fmt=StrMethodFormatter('{x:.2f}'),grp="type",
                                        ttl="B: EBITDA (%)")
    sns.barplot(data=data,x=left_lbl.x,y=left_lbl.y,hue=left_lbl.grp,dodge=False,ax=ax[0])
    sns.lineplot(data=data,x=right_lbl.x,y=right_lbl.y,hue=right_lbl.grp,ax=ax[1])
    sns.scatterplot(data=data,x=right_lbl.x,y=right_lbl.y,color="gray",ax=ax[1])
    ax[0].yaxis.set_major_formatter(left_lbl.y_fmt)
    ax[1].yaxis.set_major_formatter(right_lbl.y_fmt)
    set_labels_format(ax[0],left_lbl)
    set_labels_format(ax[1],right_lbl)
    fig.suptitle(chart_ttl)
    graph_settings(ax)

def plot_unlevered_cashflows(data:pd.DataFrame,chart_ttl:str,size:Tuple[int]=(8,6)):
    fig,ax = plt.subplots(1,1,figsize=size)
    lbl: ChartLabels = ChartLabels(x="year",xlab="",y="UFCF",ylab="USD in thousands",
                                   y_fmt=StrMethodFormatter('{x:,.0f}'),grp="",ttl=chart_ttl)
    plt.stackplot(data[lbl.x].values,data["PV of UFCF"].values,
                  data["UFCF"].values-data["PV of UFCF"].values,
                  labels=["Present value of UFCF","UFCF"])
    plt.legend(loc='upper right')
    ax.yaxis.set_major_formatter(lbl.y_fmt)
    set_labels_format(ax,lbl)
    sns.set_theme(style="whitegrid")