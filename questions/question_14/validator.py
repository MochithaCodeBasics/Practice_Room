"""
Validator for Question 1: Neural Network from Scratch (NumPy)
"""
import pandas as pd
import numpy as np
import os
from validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    get_performance_level
)

# ================================
# Question-Specific Configuration
# ================================
REQUIRED_METRICS = ['accuracy', 'final_loss']
METRIC_THRESHOLDS = {
    'accuracy': {'min': 0.80, 'valid_range': (0, 1)},  # Better than random (0.5)
    'final_loss': {'max': 0.8, 'valid_range': (0, np.inf)}  # Shows model trained
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.80, 'good': 0.70}


def validate(user_module,user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 1.
    
    Parameters
    ----------
    user_module : types.SimpleNamespace
        Module containing user's code (with main() function and other variables)
    user_df : pd.DataFrame, optional
        Pre-extracted DataFrame from user's output. If provided, skips calling main().
        If None, will call user_module.main() to get the result.
    user_code : str, optional
        User's source code for implementation verification
    
    Returns
    -------
    str
        Validation message with success/failure feedback
    """
    try:
        # 1. Get result DataFrame (from user_df or by calling main())
        if user_df is not None:
            result = user_df
        else:
            try:
                result = user_module.main()
                if not isinstance(result, pd.DataFrame):
                    return "❌ main() must return a pandas DataFrame. Return only the result DataFrame."
            except Exception as e:
                return f"❌ main() failed: {str(e)}"
        # 2. Validate implementation (e.g., check for NumPy usage)
        if user_code is not None:
            if 'import torch' in user_code or 'from torch' in user_code or 'import tensorflow' in user_code or 'from tensorflow' in user_code:
                return "❌ Your implementation should use NumPy only, not PyTorch or other deep learning libraries."
            if 'numpy' not in user_code and 'np.' not in user_code:
                return "❌ Your implementation should use NumPy for array operations."

        # 3. Validate result structure
        error = check_result_structure(result, REQUIRED_METRICS)
        if error:
            return error
        
        # 4. Extract metrics
        error, metrics = extract_metrics(result, REQUIRED_METRICS)
        if error:
            return error
        
        # 5. Check metric thresholds
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            error = check_metric_threshold(
                metric_name, metrics[metric_name],
                min_val=thresholds.get('min'),
                max_val=thresholds.get('max'),
                valid_range=thresholds.get('valid_range')
            )
            if error:
                # Add helpful hints for common issues
                if metric_name == 'accuracy' and metrics[metric_name] < 0.55:
                    return f"{error}\n💡 Hint: Accuracy barely better than random (0.5). Check your backpropagation implementation."
                elif metric_name == 'final_loss' and metrics[metric_name] > 0.8:
                    return f"{error}\n💡 Hint: Loss is too high. Did your model train? Check learning rate and number of epochs."
                return error
        
        # 6. Success!
        perf_level = get_performance_level(metrics['accuracy'], PERFORMANCE_THRESHOLDS)
        return (
            f"✅ Correct! Your NumPy neural network works!\n"
            f"   📊 Accuracy: {metrics['accuracy']:.4f}\n"
            f"   📉 Final Loss: {metrics['final_loss']:.4f}\n"
            f"   🎯 {perf_level} performance\n"
            f"   🧠 Well done implementing forward and backward propagation from scratch!"
        )
    
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"