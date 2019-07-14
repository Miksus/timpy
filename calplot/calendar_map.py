import calendar as calendar_

import seaborn as sns
import numpy as np
import pandas as pd



def annotate_dates(ax, dates, n_weeks):
    # Modified from https://github.com/mwaskom/seaborn/blob/master/seaborn/matrix.py 
    # class HeatMapper method _annotate_heatmap
    xpos, ypos = np.meshgrid(np.arange(7) + .5, np.arange(n_weeks) + .5)
    
    for x, y, val in zip(xpos.flat, ypos.flat, dates.day):
        text_kwargs = dict(color="k", ha="center", va="center")
        ax.text(x, y, val, **text_kwargs)

def generate_calendar_frame(dates=None, values=None, data=None, *, dayofweek_labels="name", show_year=True, show_month=True, show_week=True):
    if isinstance(data, pd.Series) and isinstance(data.index, pd.DatetimeIndex):
        # Time series
        data = data.sort_index()
        values = data.values
        dates = data.index if dates is None else dates
    elif isinstance(data, pd.DataFrame):
        values = data[values]
        dates = data.index if dates is None else dates
    
    # Core
    df_cal = pd.DataFrame(values, index=dates, columns=["Values"]) #data.copy().to_frame()
    
    df_cal["day of week"] = dates.dayofweek
    df_cal["week of year"] = dates.weekofyear
    
    # unstack do not keep the order, preserved manually
    weekofday_order = dates.weekofyear.unique()
    
    df_cal = df_cal.set_index(["week of year", "day of week"])
    df_cal = df_cal.unstack("day of week")["Values"]
    df_cal = df_cal.reindex(weekofday_order)
    
    
    # Additional formatting
    # Columns
    if dayofweek_labels is None:
        pass
    if dayofweek_labels.lower() == "name":
        df_cal.columns = [calendar_.day_name[num] for num in df_cal.columns]
    elif dayofweek_labels.lower() == "abbr":
        df_cal.columns = [calendar_.day_abbr[num] for num in df_cal.columns]
    elif isinstance(dayofweek_labels, str):
        raise KeyError(f"Unknown label type: {dayofweek_labels}")
    
    
    # Indexes
    bow = (dates + pd.tseries.offsets.Week(weekday=0)).unique()
    weeks = df_cal.index
    df_cal = df_cal.reset_index(drop=True)

    index_labels = []
    if show_year:
        years = bow.year
        df_cal = df_cal.set_index(years, append=True)
        index_labels += ["Year"]

    if show_month:
        months = bow.month_name() if show_month == "name" else bow.strftime("%b") if show_month == "abbr" else bow.month
        df_cal = df_cal.set_index(months, append=True)
        index_labels += ["Month"]
    
    if show_week:
        df_cal = df_cal.set_index(weeks, append=True)
        index_labels += ["Week"]

    if index_labels:
        df_cal = df_cal.reset_index(level=0, drop=True)
        df_cal.index.names = index_labels
    return df_cal


def calendar(timeseries, kwds_calendar=None, **kwargs):
    
    start = timeseries.index.min() + pd.tseries.offsets.Week(weekday=0)
    stop = timeseries.index.max() + pd.tseries.offsets.Week(weekday=0) + pd.tseries.offsets.Week(weekday=6)
    timeseries = timeseries.reindex(pd.date_range(start, stop, freq="D"))
    
    dates = timeseries.index
    values = timeseries.values
    
    if kwds_calendar is None:
        kwds_calendar = {}
        
    kwds_plot = dict(
        square=True, 
        linewidths=1,
        annot=False,#generate_calendar_frame(values=dates.day, dates=dates).values if kwds_calendar.get("show_dates", True) else None,
        linecolor="black"
    )
    kwds_plot.update(kwargs)
    
    df_calendar = generate_calendar_frame(dates=dates, values=values, **kwds_calendar)
    ax = sns.heatmap(
        df_calendar,
        **kwds_plot
    )
    
    ax.tick_params(axis="y", labelrotation=0)
    ax.set_facecolor('white')
    if kwds_calendar.get("show_dates", True):
        annotate_dates(ax, dates, n_weeks=df_calendar.shape[0])
    return ax