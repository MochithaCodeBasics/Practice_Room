import pandas as pd
import numpy as np


def validate(user_module) -> str:
    """
    Validates the create_pairplot function.
    
    Checks:
    1. Function existence and callable signature
    2. Returned object is a matplotlib Figure
    3. Number of plotted variables equals len(cols)
    4. Figure object exists and is valid
    """
    try:
        # Check if function exists
        if not hasattr(user_module, "create_pairplot"):
            return "❌ Function `create_pairplot` is not defined."

        func = user_module.create_pairplot

        # Check if it's callable
        if not callable(func):
            return "❌ `create_pairplot` is not callable."

        # Create test DataFrame
        np.random.seed(42)
        test_df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45, 50, 55, 60],
            'annual_income': [50000, 60000, 70000, 80000, 90000, 85000, 75000, 65000],
            'credit_score': [650, 700, 720, 680, 750, 710, 690, 730],
            'monthly_spend': [2000, 2500, 3000, 2800, 3200, 2900, 2700, 3100],
            'city_tier': ['Tier1', 'Tier2', 'Tier1', 'Tier3', 'Tier2', 'Tier1', 'Tier3', 'Tier2']
        })

        # Test Case 1: Basic pairplot without hue
        cols = ['age', 'annual_income', 'credit_score']
        result = func(test_df, cols)

        # Check if result is a matplotlib Figure
        try:
            from matplotlib.figure import Figure
            if not isinstance(result, Figure):
                return f"❌ Expected matplotlib Figure, got {type(result).__name__}"
        except ImportError:
            return "⚠️ matplotlib is required for this question."

        # Check if figure has axes (confirming pairplot was created)
        if not hasattr(result, 'axes') or len(result.axes) == 0:
            return "❌ Figure has no axes. Pairplot may not have been created correctly."

        # For a pairplot with n variables, we expect at least n*n subplots
        # Note: seaborn may add extra axes for legends/colorbar, so we check for >= 
        expected_axes = len(cols) * len(cols)
        actual_axes = len(result.axes)
        if actual_axes < expected_axes:
            return f"❌ Expected at least {expected_axes} subplots for {len(cols)} columns, got {actual_axes}."

        # Test Case 2: Pairplot with hue
        result_with_hue = func(test_df, ['age', 'annual_income'], hue='city_tier')

        if not isinstance(result_with_hue, Figure):
            return f"❌ With hue parameter: Expected matplotlib Figure, got {type(result_with_hue).__name__}"

        # Test Case 3: DataFrame with missing values
        test_df_with_nan = test_df.copy()
        test_df_with_nan.loc[0, 'age'] = np.nan
        test_df_with_nan.loc[1, 'annual_income'] = np.nan

        result_with_nan = func(test_df_with_nan, ['age', 'annual_income'])
        
        if not isinstance(result_with_nan, Figure):
            return "❌ Function should handle missing values and still return a Figure."

        # Close all figures to prevent memory leaks
        import matplotlib.pyplot as plt
        plt.close('all')

        # -------------------------------------------------
        # Hidden Test Case 4: Only 2 columns (smaller grid)
        # -------------------------------------------------
        result_two_cols = func(test_df, ['monthly_spend', 'credit_score'])

        if not isinstance(result_two_cols, Figure):
            return f"❌ Hidden test: Expected matplotlib Figure for 2 columns, got {type(result_two_cols).__name__}"

        expected_axes_2 = 2 * 2
        actual_axes_2 = len(result_two_cols.axes)
        if actual_axes_2 < expected_axes_2:
            return f"❌ Hidden test: Expected at least {expected_axes_2} subplots for 2 columns, got {actual_axes_2}."

        plt.close('all')

        # -------------------------------------------------
        # Hidden Test Case 5: Completely different DataFrame
        # -------------------------------------------------
        hidden_df = pd.DataFrame({
            'height': [160, 170, 175, 180, 165, 172],
            'weight': [55, 70, 78, 85, 60, 68],
            'bmi': [21.5, 24.2, 25.5, 26.2, 22.0, 23.0],
            'group': ['A', 'B', 'A', 'B', 'A', 'B']
        })

        result_hidden = func(hidden_df, ['height', 'weight', 'bmi'], hue='group')

        if not isinstance(result_hidden, Figure):
            return f"❌ Hidden test: Expected matplotlib Figure for new DataFrame, got {type(result_hidden).__name__}"

        expected_axes_h = 3 * 3
        actual_axes_h = len(result_hidden.axes)
        if actual_axes_h < expected_axes_h:
            return f"❌ Hidden test: Expected at least {expected_axes_h} subplots for 3 columns, got {actual_axes_h}."

        plt.close('all')

        return "✅ Correct! All test cases passed successfully."

    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
