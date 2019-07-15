# Timpy

> Time series plotting for Python


---

## Example

```python
import pandas as pd
import timpy as tplt

series = pd.Series([1,2,3,4], index=["2019-07-01", "2019-07-03", "2019-07-14", "2019-08-01"])
tplt.calendar(series)
```