import calendar as calendar_

import seaborn as sns
import numpy as np
import pandas as pd


class _CalendarFrame:

    def __init__(self, show_year, show_month, show_week, dayofweek_labels, **kwargs):
        self.show_year = show_year
        self.show_month = show_month
        self.show_week = show_week

        self.dayofweek_labels = dayofweek_labels


    def to_calendar_dataframe(self, dates, values):
        # Core
        df_cal = pd.DataFrame(values, index=dates, columns=["Values"])
        
        df_cal["day of week"] = dates.dayofweek
        df_cal["week"] = dates - pd.to_timedelta(dates.dayofweek, unit="d")
        
        df_cal = df_cal.set_index(["week", "day of week"])
        df_cal = df_cal.unstack("day of week")["Values"]
        
        df_cal = self._format_columns(df_cal)
        df_cal = self._format_indexes(df_cal, dates)
        return df_cal
        
    def _format_columns(self, df_calendar):
        dow_labels = self.dayofweek_labels

        if dow_labels is None:
            pass
        elif isinstance(dow_labels, str):
            if dow_labels == "name":
                # Monday, Tuesday, Wednesday etc.
                df_calendar.columns = [calendar_.day_name[num] for num in df_calendar.columns]
            elif dow_labels == "abbr":
                # Mon, Tue, Wed etc.
                df_calendar.columns = [calendar_.day_abbr[num] for num in df_calendar.columns]
            else:
                raise KeyError(f"Unknown label type: {dow_labels}")
        else:
            df_calendar.columns = dow_labels
        return df_calendar
        
    def _format_indexes(self, df_calendar, dates):
        
        # Indexes
        bow = pd.date_range(start=dates.min(), end=dates.max(), freq="W-MON")
        weeks = df_calendar.index
        df_calendar = df_calendar.reset_index(drop=True)

        index_labels = []

        if self.show_year:
            years = bow.year
            df_calendar = df_calendar.set_index(years, append=True)
            index_labels += ["Year"]

        if self.show_month:
            if self.show_month == "name":
                # January, Febraury, etc.
                months = bow.month_name()
            elif self.show_month == "abbr":
                # Jan, Feb, etc.
                months = bow.strftime("%b")
            else:
                months = bow.month

            df_calendar = df_calendar.set_index(months, append=True)
            index_labels += ["Month"]
        
        if self.show_week:
            weeks = bow.weekofyear
            df_calendar = df_calendar.set_index(weeks, append=True)
            index_labels += ["Week"]

        if index_labels:
            df_calendar = df_calendar.reset_index(level=0, drop=True)
            df_calendar.index.names = index_labels
        return df_calendar

def _format_index(data:pd.Series, start_date=None, end_date=None):
    start_date = data.index.min() if start_date is None else pd.to_datetime(start_date)
    start = pd.tseries.offsets.Week(weekday=0).rollback(start_date)
    
    end_date = data.index.max() if end_date is None else pd.to_datetime(end_date)
    end = pd.tseries.offsets.Week(weekday=6).rollforward(end_date)

    return data.reindex(pd.date_range(start, end, freq="D"))
    
def _annotate_dates(ax, dates, n_weeks):
    # Modified from https://github.com/mwaskom/seaborn/blob/master/seaborn/matrix.py 
    # class HeatMapper method _annotate_heatmap
    xpos, ypos = np.meshgrid(np.arange(7) + .5, np.arange(n_weeks) + .5)
    
    for x, y, val in zip(xpos.flat, ypos.flat, dates.day):
        text_kwargs = dict(color="k", ha="center", va="center")
        ax.text(x, y, val, **text_kwargs)

def calendar(data, start_date=None, end_date=None, show_dates=True,
            show_year=True, show_month=True, show_week=True, dayofweek_labels="name", **kwargs):
    """Plot numerical timeseries to calendar-like heatmap
    
    Arguments:
        data {pd.Series}
            Time series to plot. Must contain numerical data.
    
    Keyword Arguments:
        start_date {str, datetime like}
            Start date of the calendar. 
            Default: start date of the data
        end_date {str, datetime like} -- 
            End date of the calendar. 
            Default: end date of the data
        show_dates : {bool}
            Whether to annotate dates on the calendar. Default: True
        show_year : {bool}
            Whether to show year or not (default: {True})
        show_month : {bool or "name", "abbr"}
            Definition how to show the months.
            "name": full name of the month (January, February, ...)
            "abbr": abbreviation of the month (Jan, Feb, ...) 
            Default: "name"
        show_week : {bool}
            Whether to show week number or not (default: {True})
        dayofweek_labels : {"name", "abbr" or List[str]}
            Labels for the week days
            "name" : full name of the week day (Monday, Tuesday, ...)
            "abbr" : abbretiation of the week day (Mon, Tue, ...) 
            Defautl : "name" (default: {"name"})
        kwargs -- other keyword arguments
            All other arguments are passed to ``seaborn.heatmap``

    Returns:
        ax -- Matplotlib Axes
            Axes object with the calendar
    """

    kwds_plot = dict(
        square=True, 
        linewidths=1,
        annot=False,
        linecolor="black"
    )
    kwds_plot.update(kwargs)

    cal_kws = dict(
        show_year=show_year,
        show_month=show_month,
        show_week=show_week,
        dayofweek_labels=dayofweek_labels
    )

    data = _format_index(data, start_date, end_date)
    
    dates = data.index
    values = data.values

    formatter = _CalendarFrame(**cal_kws)
    df_calendar = formatter.to_calendar_dataframe(dates, values)
    ax = sns.heatmap(
        df_calendar,
        **kwds_plot
    )
    
    ax.tick_params(axis="y", labelrotation=0)
    ax.set_facecolor('white')

    if show_dates:
        _annotate_dates(ax, dates, n_weeks=df_calendar.shape[0])
    return ax