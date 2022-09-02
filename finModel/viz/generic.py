from matplotlib.ticker import StrMethodFormatter
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


@dataclass
class ChartLabels:
    x: str
    xlab: str
    y: str
    ylab: str
    y_fmt: StrMethodFormatter
    grp: str
    ttl: str


def graph_settings(ax:np.ndarray):
    sns.set_theme(style="whitegrid")
    for a in ax:
        a.legend().set_title("")


def set_labels_format(ax:plt.Axes,lbl: ChartLabels):
    ax.set_xlabel(lbl.xlab)
    ax.set_ylabel(lbl.ylab)
    ax.set_title(lbl.ttl)
    ax.yaxis.set_major_formatter(lbl.y_fmt)





