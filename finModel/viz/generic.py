from matplotlib.ticker import StrMethodFormatter
from dataclasses import dataclass
from typing import Dict, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

Colors: Dict[str,str] = {"cobalt blue": "#0047AB",
                         "light blue": "#ADD8E6",
                         "gold": "#FFD700",
                         "blue gray": "#7393B3",
                         "beige": "#F5F5DC"}

@dataclass
class ChartLabels:
    x: str
    xlab: str
    y: str
    ylab: str
    grp: str
    ttl: str
    y_fmt: Optional[str] = None


def graph_settings(ax:np.ndarray,legend:bool=True):
    sns.set_theme(style="whitegrid")
    if legend is True:
        for a in ax:
            a.legend().set_title("")


def set_labels_format(ax:plt.Axes,lbl: ChartLabels):
    ax.set_xlabel(lbl.xlab)
    ax.set_ylabel(lbl.ylab)
    ax.set_title(lbl.ttl)
    if lbl.y_fmt is not None:
        ax.yaxis.set_major_formatter(StrMethodFormatter(lbl.y_fmt))
