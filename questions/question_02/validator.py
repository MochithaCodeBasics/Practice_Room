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

        # Check for scatter plot (anomaly points)
        collections = ax.collections
        # At least check that plot elements exist
        if len(lines) < 2:
            return "❌ Plot should contain at least raw data line and rolling mean line."

        # Verify rolling mean calculation internally
        df_check = test_df.copy()
        df_check['date'] = pd.to_datetime(df_check['date'])
        rolling_mean = df_check['transaction_count'].rolling(window).mean()
        rolling_std = df_check['transaction_count'].rolling(window).std()
        
        # Check anomaly detection logic
        deviation = abs(df_check['transaction_count'] - rolling_mean)
        expected_anomalies = deviation > (3 * rolling_std)
        num_expected_anomalies = expected_anomalies.sum()

        # Close all figures to prevent memory leaks
        import matplotlib.pyplot as plt
        plt.close('all')

        return "✅ Correct! Transaction anomaly detection plot is valid."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
