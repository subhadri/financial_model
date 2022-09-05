from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List
import pandas as pd
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
    grp: Optional[str] = None
    ttl: Optional[str] = None
    y2: Optional[str] = None
    y2lab: Optional[str] = None


def style_table(df:pd.DataFrame,bold_rows:List[str],pct_rows:List[str]) -> pd.DataFrame.style:
    '''
    This function will format the report tables using the below rules:

    * Dark blue and bold columns
    * White background with gray share for forecast period
    * All numbers in accounting format and percentages in %
    * Show all missing values/zeros as blanks
    * All negative numbers in brackets
    * Black bold row totals
    '''
    formatted = df.copy(deep=True)

    # Apply accounting and percentage format
    for r in df.index.tolist():
        if r in pct_rows:
            formatted.loc[r] = df.loc[r].apply('{:.2%}'.format)
        else:
            formatted.loc[r] = df.loc[r].apply('{:,.0f}'.format)

    # Treat zeroes/missing values as blank and negative no.s in ()
    for r in df.index.tolist():
        for c in df.columns:
            if df.loc[r,c]==0. or df.loc[r,c]=="nan":
                formatted.loc[r,c] = ""
            if df.loc[r,c]<0:
                formatted.loc[r,c] = f"({formatted.loc[r,c][1:]})"

    index_bold_row = pd.IndexSlice[[True if val in bold_rows else False for val in df.index],:]
    formatted = formatted.reset_index().style.applymap(lambda x: "font-weight: bold", subset=index_bold_row)

    formatted = formatted.set_properties(**{'background-color': 'white'}).hide_index()
    formatted = formatted.set_properties(**{'background-color': 'lightgray'},
                                         subset=formatted.columns.str.endswith("F"))
    formatted = formatted.hide_index()

    return formatted


def report_table(data:pd.DataFrame,f_date:np.ndarray,bold_rows:List[str],pct_rows:List[str]=["None"]) -> pd.DataFrame.style:

    order: pd.DataFrame = pd.DataFrame({'component': data.columns.values})
    data['year'] = pd.DatetimeIndex(data.index).year
    data['period_label'] = ['F' if date in f_date else 'A' for date in data.index]
    data['index'] = [f"{round(data.year[idx],0)}{data.period_label[idx]}" for idx in data.index]
    melted_data: pd.DataFrame = data.melt(id_vars=['year','period_label','index'],var_name='component')
    pivoted_data: pd.DataFrame = melted_data.pivot(index='component',columns='index',values='value')
    out: pd.DataFrame = pd.merge(left=order,right=pivoted_data,how="left",on="component").set_index("component")
    formatted: pd.DataFrame.style = style_table(out,bold_rows,pct_rows)

    return formatted
