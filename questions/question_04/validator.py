import pandas as pd
import math
import os


def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def validate(result, plot=None, expected_path=None) -> str:
    """
    Validates:
      - result: DataFrame with month, revenue, mom_growth_pct
      - plot: matplotlib Axes used to draw the line chart (if provided)
    Robust to platforms that call validate(result, expected_path) or validate(result).
    """
    try:
        # -------------------------------------------------
        # Fix argument shifting: validate(result, expected_path)
        # -------------------------------------------------
        # If plot is a string path and expected_path is missing, treat it as expected_path
        if isinstance(plot, str) and expected_path is None:
            expected_path = plot
            plot = None

        # -------------------------------------------------
        # Load original data
        # -------------------------------------------------
        base_dir = os.path.dirname(__file__)
        data_path = os.path.join(base_dir, "data.csv")

        if not os.path.exists(data_path):
            return "⚠️ Validation error: data.csv not found."

        data = pd.read_csv(data_path)

        # -------------------------------------------------
        # 1) Validate result DataFrame
        # -------------------------------------------------
        if not isinstance(result, pd.DataFrame):
            return "❌ `result` must be a pandas DataFrame."

        required_cols = ["month", "revenue", "mom_growth_pct"]
        for col in required_cols:
            if col not in result.columns:
                return f"❌ Missing required column: `{col}`"

        # -------------------------------------------------
        # 2) Validate plot (ONLY if the platform provides it)
        # -------------------------------------------------
        # If your platform truly requires plot, change this block to fail when plot is None.
        if plot is not None:
            try:
                from matplotlib.axes import Axes
                if not isinstance(plot, Axes):
                    return f"❌ `plot` must be a matplotlib Axes object, got {type(plot).__name__}."
                # optional: ensure a line exists
                if len(getattr(plot, "lines", [])) == 0:
                    return "❌ Plot Axes found, but no line was drawn."
            except ImportError:
                return "⚠️ matplotlib is required for this question."

        # -------------------------------------------------
        # 3) Compute expected values
        # -------------------------------------------------
        df = data.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["month"] = df["order_date"].dt.to_period("M").astype(str)

        expected = (
            df.groupby("month", as_index=False)["amount"]
              .sum()
              .rename(columns={"amount": "revenue"})
              .sort_values("month")
              .reset_index(drop=True)
        )
        expected["mom_growth_pct"] = expected["revenue"].pct_change() * 100
        expected["revenue"] = expected["revenue"].round(2)
        expected["mom_growth_pct"] = expected["mom_growth_pct"].round(2)

        # -------------------------------------------------
        # 4) Compare with user result
        # -------------------------------------------------
        user_sorted = result.sort_values("month").reset_index(drop=True)

        if len(user_sorted) != len(expected):
            return f"❌ Expected {len(expected)} rows, got {len(user_sorted)} rows."

        for i in range(len(expected)):
            if expected.loc[i, "month"] != str(user_sorted.loc[i, "month"]):
                return f"❌ Row {i}: month mismatch"

            if not _approx_equal(expected.loc[i, "revenue"], user_sorted.loc[i, "revenue"]):
                return f"❌ Row {i}: revenue mismatch"

            if not _approx_equal(expected.loc[i, "mom_growth_pct"], user_sorted.loc[i, "mom_growth_pct"]):
                return f"❌ Row {i}: mom_growth_pct mismatch"

        # If plot is required by spec but platform didn't pass it, you can enforce here:
        # if plot is None:
        #     return "❌ Missing `plot` object. Please assign matplotlib Axes to `plot`."

        return "✅ Correct! Monthly revenue analysis is valid."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
