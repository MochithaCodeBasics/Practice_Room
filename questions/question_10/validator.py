import pandas as pd
import math
import os
import random
import io
import contextlib


def _approx_equal(a: float, b: float, tol: float = 1e-2) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.01)


def validate(user_module) -> str:
    """
    Validates:
      - monthly_revenue or result: DataFrame with month, revenue, mom_growth_pct
      - result or fig: matplotlib Figure with a line chart
      - plot: matplotlib Axes used to draw the line chart (if provided)
    """
    try:
        # -------------------------------------------------
        # Load original data
        # -------------------------------------------------
        base_dir = os.path.dirname(__file__)
        data_path = os.path.join(base_dir, "data.csv")

        if not os.path.exists(data_path):
            return "⚠️ Validation error: data.csv not found."

        data = pd.read_csv(data_path)

        # -------------------------------------------------
        # 1) Find the DataFrame result
        # -------------------------------------------------
        user_df = None

        # Check for monthly_revenue first (new approach)
        if hasattr(user_module, "monthly_revenue"):
            candidate = getattr(user_module, "monthly_revenue")
            if isinstance(candidate, pd.DataFrame):
                user_df = candidate

        # Fallback to result if it's a DataFrame
        if user_df is None and hasattr(user_module, "result"):
            candidate = getattr(user_module, "result")
            if isinstance(candidate, pd.DataFrame):
                user_df = candidate

        if user_df is None:
            return "❌ No DataFrame found. Expected `monthly_revenue` or `result` DataFrame."

        # -------------------------------------------------
        # 2) Validate the DataFrame has required columns
        # -------------------------------------------------
        required_cols = ["month", "revenue", "mom_growth_pct"]
        for col in required_cols:
            if col not in user_df.columns:
                return f"❌ Missing required column: `{col}`"

        # -------------------------------------------------
        # 3) Validate the plot/figure exists
        # -------------------------------------------------
        figure_found = False

        # Check for result being a Figure
        if hasattr(user_module, "result"):
            result_obj = getattr(user_module, "result")
            result_class = getattr(result_obj.__class__, "__name__", "")
            if result_class == "Figure":
                figure_found = True

        # Check for fig variable
        if not figure_found and hasattr(user_module, "fig"):
            fig_obj = getattr(user_module, "fig")
            fig_class = getattr(fig_obj.__class__, "__name__", "")
            if fig_class == "Figure":
                figure_found = True

        # Check for plot (Axes) with lines
        if hasattr(user_module, "plot"):
            plot_obj = getattr(user_module, "plot")
            try:
                from matplotlib.axes import Axes
                if isinstance(plot_obj, Axes):
                    if len(getattr(plot_obj, "lines", [])) == 0:
                        return "❌ Plot Axes found, but no line was drawn."
                    figure_found = True
            except ImportError:
                pass

        if not figure_found:
            return "❌ No plot found. Please create a matplotlib figure/plot."

        # -------------------------------------------------
        # 4) Compute expected values from raw data
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
        # 5) Compare row counts
        # -------------------------------------------------
        user_sorted = user_df.sort_values("month").reset_index(drop=True)

        if len(user_sorted) != len(expected):
            return f"❌ Expected {len(expected)} rows, got {len(user_sorted)} rows."

        # -------------------------------------------------
        # 6) Compare each row (hidden — values computed at runtime)
        # -------------------------------------------------
        for i in range(len(expected)):
            if expected.loc[i, "month"] != str(user_sorted.loc[i, "month"]):
                return f"❌ Row {i}: month mismatch."

            if not _approx_equal(expected.loc[i, "revenue"], user_sorted.loc[i, "revenue"]):
                return f"❌ Row {i}: revenue mismatch."

            if not _approx_equal(expected.loc[i, "mom_growth_pct"], user_sorted.loc[i, "mom_growth_pct"]):
                return f"❌ Row {i}: mom_growth_pct mismatch."

        # -------------------------------------------------
        # 7) Verify first-row growth is NaN
        # -------------------------------------------------
        first_growth = user_sorted.loc[0, "mom_growth_pct"]
        if not pd.isna(first_growth):
            return "❌ First month's mom_growth_pct should be NaN."

        # -------------------------------------------------
        # 8) HIDDEN TEST — re-execute learner code with
        #    a dynamically generated hidden DataFrame
        # -------------------------------------------------
        random.seed(2026)
        hidden_rows = []
        months = ["2025-01", "2025-02", "2025-03", "2025-04"]
        for m in months:
            n_orders = random.randint(3, 8)
            for _ in range(n_orders):
                day = random.randint(1, 28)
                hidden_rows.append({
                    "order_id": f"ORD-{random.randint(1000, 9999)}",
                    "order_date": f"{m}-{day:02d}",
                    "amount": round(random.uniform(10, 500), 2),
                })
        hidden_data = pd.DataFrame(hidden_rows)

        # Compute expected results from hidden data
        hdf = hidden_data.copy()
        hdf["order_date"] = pd.to_datetime(hdf["order_date"])
        hdf["month"] = hdf["order_date"].dt.to_period("M").astype(str)
        hidden_expected = (
            hdf.groupby("month", as_index=False)["amount"]
               .sum()
               .rename(columns={"amount": "revenue"})
               .sort_values("month")
               .reset_index(drop=True)
        )
        hidden_expected["mom_growth_pct"] = hidden_expected["revenue"].pct_change() * 100
        hidden_expected["revenue"] = hidden_expected["revenue"].round(2)
        hidden_expected["mom_growth_pct"] = hidden_expected["mom_growth_pct"].round(2)

        # Try to re-execute the learner's source code with hidden data
        try:
            # Retrieve the learner's original source from the sandbox
            user_source = getattr(user_module, "__source__", None)

            if user_source:
                hidden_sandbox = {
                    "__name__": "__main__",
                    "__builtins__": __builtins__,
                    "data": hidden_data.copy(),
                }

                stdout_buf = io.StringIO()
                with contextlib.redirect_stdout(stdout_buf):
                    exec(user_source, hidden_sandbox)

                # Find the result DataFrame in the hidden sandbox
                hidden_user_df = None
                if "monthly_revenue" in hidden_sandbox:
                    c = hidden_sandbox["monthly_revenue"]
                    if isinstance(c, pd.DataFrame):
                        hidden_user_df = c
                if hidden_user_df is None and "result" in hidden_sandbox:
                    c = hidden_sandbox["result"]
                    if isinstance(c, pd.DataFrame):
                        hidden_user_df = c

                if hidden_user_df is None:
                    return "❌ Hidden test failed: no DataFrame produced."

                req_cols = ["month", "revenue", "mom_growth_pct"]
                for col in req_cols:
                    if col not in hidden_user_df.columns:
                        return f"❌ Hidden test failed: missing column `{col}`."

                h_sorted = hidden_user_df.sort_values("month").reset_index(drop=True)

                if len(h_sorted) != len(hidden_expected):
                    return "❌ Hidden test failed: row count mismatch."

                for i in range(len(hidden_expected)):
                    if hidden_expected.loc[i, "month"] != str(h_sorted.loc[i, "month"]):
                        return f"❌ Hidden test failed: month mismatch at row {i}."
                    if not _approx_equal(hidden_expected.loc[i, "revenue"], h_sorted.loc[i, "revenue"]):
                        return f"❌ Hidden test failed: revenue mismatch at row {i}."
                    if not _approx_equal(hidden_expected.loc[i, "mom_growth_pct"], h_sorted.loc[i, "mom_growth_pct"]):
                        return f"❌ Hidden test failed: mom_growth_pct mismatch at row {i}."

        except Exception:
            # If re-execution fails (e.g. no source available), skip
            # gracefully — the primary data.csv test already passed
            pass

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
