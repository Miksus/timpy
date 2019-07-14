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
        df_cal = pd.DataFrame(values, index=dates, columns=["Values"]) #data.copy().to_frame()
        
        df_cal["day of week"] = dates.dayofweek
        df_cal["week of year"] = dates.strftime('%Y-%W') # BUG: new year week causes multiple rows: 2019-12-30 --> 2019-55 and 2020-01-01 --> 2020-01
        
        # unstack does not keep the order, preserved manually
        weekofyear_order = dates.weekofyear.unique()
        
        df_cal = df_cal.set_index(["week of year", "day of week"])
        df_cal = df_cal.unstack("day of week")["Values"]
        #df_cal = df_cal.reindex(weekofyear_order)
        
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
                raise KeyError(f"Unknown label type: {dayofweek_labels}")
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
            print(df_calendar.index.min(), df_calendar.index.max())
            print(df_calendar)
            print(years.min(), years.max(), years)
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

def calendar(data=None, cal_kws=None, start_date=None, end_date=None, **kwargs):


    kwds_plot = dict(
        square=True, 
        linewidths=1,
        annot=False,
        linecolor="black"
    )
    kwds_plot.update(kwargs)

    cal_kws_ = dict(
        show_year=True,
        show_month=True,
        show_week=True,
        dayofweek_labels="name"
    )
    cal_kws_.update(cal_kws if cal_kws is not None else {})

    data = _format_index(data, start_date, end_date)
    
    dates = data.index
    values = data.values

    formatter = _CalendarFrame(**cal_kws_)
    df_calendar = formatter.to_calendar_dataframe(dates, values)
    print(df_calendar)
    ax = sns.heatmap(
        df_calendar,
        **kwds_plot
    )
    
    ax.tick_params(axis="y", labelrotation=0)
    ax.set_facecolor('white')

    if cal_kws_.get("show_dates", True):
        _annotate_dates(ax, dates, n_weeks=df_calendar.shape[0])
    return ax