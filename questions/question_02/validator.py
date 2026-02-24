import pandas as pd
import numpy as np
import os


def validate(user_module) -> str:
    """
    Validates the plot_transactions_with_rolling_mean function.
    
    Checks:
    1. Rolling mean computed correctly
    2. Anomaly points identified correctly
    3. Figure object contains multiple plotted lines
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "plot_transactions_with_rolling_mean"):
            return "❌ Function `plot_transactions_with_rolling_mean` is not defined."

        func = user_module.plot_transactions_with_rolling_mean

        # Check if it's callable
        if not callable(func):
            return "❌ `plot_transactions_with_rolling_mean` is not callable."

        # Load test data
        base_dir = os.path.dirname(__file__)
        data_path = os.path.join(base_dir, "data.csv")
        
        if os.path.exists(data_path):
            test_df = pd.read_csv(data_path)
        else:
            # Create test data if file doesn't exist
            np.random.seed(42)
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            transactions = np.random.normal(100, 10, 30).astype(int)
            # Add anomalies
            transactions[10] = 250  # Anomaly
            transactions[20] = 300  # Anomaly
            test_df = pd.DataFrame({
                'date': dates.strftime('%Y-%m-%d'),
                'transaction_count': transactions
            })

        window = 5
        result = func(test_df.copy(), window)

        # Check if result is a matplotlib Figure
        try:
            from matplotlib.figure import Figure
            if not isinstance(result, Figure):
                return f"❌ Expected matplotlib Figure, got {type(result).__name__}"
        except ImportError:
            return "⚠️ matplotlib is required for this question."

        # Check if figure has axes
        if not hasattr(result, 'axes') or len(result.axes) == 0:
            return "❌ Figure has no axes."

        ax = result.axes[0]

        # Check for multiple lines (raw data + rolling mean)
        lines = ax.get_lines()
        if len(lines) < 2:
            return f"❌ Expected at least 2 lines (raw data and rolling mean), got {len(lines)}."

        # Verify rolling mean calculation internally
        df_check = test_df.copy()
        df_check['date'] = pd.to_datetime(df_check['date'])
        rolling_mean = df_check['transaction_count'].rolling(window).mean()
        rolling_std = df_check['transaction_count'].rolling(window).std()

        # Check anomaly detection logic
        deviation = abs(df_check['transaction_count'] - rolling_mean)
        expected_anomalies = deviation > (3 * rolling_std)
        num_expected_anomalies = int(expected_anomalies.sum())

        # Check for scatter plot (anomaly points) via collections
        collections = ax.collections
        if num_expected_anomalies > 0 and len(collections) == 0:
            return "❌ Expected anomaly points to be highlighted (scatter), but no scatter points found."

        # Validate that the number of plotted anomaly points matches expected
        if len(collections) > 0:
            # Get total number of scatter points across all collections
            total_scatter_points = sum(len(c.get_offsets()) for c in collections)
            if total_scatter_points != num_expected_anomalies:
                return (
                    f"❌ Expected {num_expected_anomalies} anomaly points, "
                    f"but found {total_scatter_points} scatter points."
                )

        # Close all figures to prevent memory leaks
        import matplotlib.pyplot as plt
        plt.close('all')

        # -------------------------------------------------
        # Hidden Test Case: Different window + synthetic data
        # -------------------------------------------------
        np.random.seed(99)
        hidden_dates = pd.date_range('2025-06-01', periods=20, freq='D')
        hidden_txns = np.array([50, 55, 48, 52, 51, 49, 53, 47, 50, 52,
                                200, 51, 48, 53, 50, 49, 52, 54, 51, 50])
        hidden_df = pd.DataFrame({
            'date': hidden_dates.strftime('%Y-%m-%d'),
            'transaction_count': hidden_txns
        })

        hidden_window = 3
        hidden_result = func(hidden_df.copy(), hidden_window)

        if not isinstance(hidden_result, Figure):
            return f"❌ Hidden test: Expected matplotlib Figure, got {type(hidden_result).__name__}"

        if not hasattr(hidden_result, 'axes') or len(hidden_result.axes) == 0:
            return "❌ Hidden test: Figure has no axes."

        hidden_ax = hidden_result.axes[0]

        hidden_lines = hidden_ax.get_lines()
        if len(hidden_lines) < 2:
            return f"❌ Hidden test: Expected at least 2 lines, got {len(hidden_lines)}."

        # Compute expected anomalies for hidden data
        hidden_df_check = hidden_df.copy()
        hidden_df_check['date'] = pd.to_datetime(hidden_df_check['date'])
        hidden_rolling_mean = hidden_df_check['transaction_count'].rolling(hidden_window).mean()
        hidden_rolling_std = hidden_df_check['transaction_count'].rolling(hidden_window).std()
        hidden_deviation = abs(hidden_df_check['transaction_count'] - hidden_rolling_mean)
        hidden_expected = int((hidden_deviation > (3 * hidden_rolling_std)).sum())

        hidden_collections = hidden_ax.collections
        if hidden_expected > 0 and len(hidden_collections) == 0:
            return "❌ Hidden test: Expected anomaly scatter points, but none found."

        if len(hidden_collections) > 0:
            hidden_scatter = sum(len(c.get_offsets()) for c in hidden_collections)
            if hidden_scatter != hidden_expected:
                return (
                    f"❌ Hidden test: Expected {hidden_expected} anomaly points, "
                    f"but found {hidden_scatter}."
                )

        plt.close('all')

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
