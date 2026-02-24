"""
Validator for Question 7: CNN for Shape Classification
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from _validator_utils import (
    check_result_structure,
    extract_metrics,
    check_metric_threshold,
    get_performance_level
)
import question

# ================================
# Question-Specific Configuration
# ================================
REQUIRED_METRICS = ['accuracy', 'macro_f1']

def get_input_variables():
    return {"get_dataset_path": question.get_dataset_path}
METRIC_THRESHOLDS = {
    'accuracy': {'min': 0.85, 'valid_range': (0, 1)},
    'macro_f1': {'min': 0.83, 'valid_range': (0, 1)},
}
PERFORMANCE_THRESHOLDS = {'excellent': 0.92, 'good': 0.88}

def validate(user_module, user_code=None, user_df=None) -> str:
    """
    Validate user's solution for Question 7.
    
    Parameters
    ----------
    user_module : types.SimpleNamespace
        Module containing user's code (with main() function and other variables)
    user_code : str, optional
        User's source code for implementation verification
    user_df : pd.DataFrame, optional
        Pre-extracted DataFrame from user's output. If provided, skips calling main().
        If None, will call user_module.main() to get the result.
    
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
                    return "❌ main() must return a pandas DataFrame with performance metrics."
            except Exception as e:
                return f"❌ main() failed: {str(e)}"
        
        # 2. Validate DataFrame structure
        if not all(col in result.columns for col in ['metric', 'value']):
            return "❌ Result DataFrame must have columns: ['metric', 'value']"
        
        # 3. Check for required metrics
        result_metrics = set(result['metric'].values)
        missing_metrics = set(REQUIRED_METRICS) - result_metrics
        if missing_metrics:
            return (
                f"❌ Missing required metrics: {missing_metrics}\n"
                f"   💡 Hint: Calculate both overall accuracy and macro-averaged F1 score"
            )
        
        # 4. Extract metrics
        metrics_dict = {}
        for _, row in result.iterrows():
            if row['metric'] in REQUIRED_METRICS:
                metrics_dict[row['metric']] = row['value']
        
        # 5. Validate metric ranges and thresholds
        errors = []
        for metric_name, thresholds in METRIC_THRESHOLDS.items():
            value = metrics_dict.get(metric_name)
            if value is None:
                continue
            
            # Check valid range
            valid_range = thresholds['valid_range']
            if not (valid_range[0] <= value <= valid_range[1]):
                errors.append(
                    f"❌ {metric_name}={value:.4f} is out of valid range {valid_range}\n"
                    f"   💡 Hint: Check your metric calculation"
                )
                continue
            
            # Check minimum threshold (without revealing it)
            min_val = thresholds.get('min')
            if min_val and value < min_val:
                if metric_name == 'accuracy':
                    errors.append(
                        f"❌ Model accuracy is below required threshold\n"
                        f"   Current: {value:.4f}\n"
                        f"   💡 Hints:\n"
                        f"      - Add more convolutional layers for better feature extraction\n"
                        f"      - Increase training epochs (try 15-20)\n"
                        f"      - Try different learning rates (e.g., 0.001)"
                    )
                elif metric_name == 'macro_f1':
                    errors.append(
                        f"❌ Macro F1 score is below required threshold\n"
                        f"   Current: {value:.4f}\n"
                        f"   💡 Hints:\n"
                        f"      - Ensure balanced class performance\n"
                        f"      - Check if all classes are predicted correctly\n"
                        f"      - Increase model capacity or training time"
                    )
        
        if errors:
            return "\n\n".join(errors)
        
        # 6. Check for CNN implementation components
        implementation_warnings = []
        if user_code:
            has_conv = 'conv2d' in user_code.lower()
            has_pool = 'pool' in user_code.lower() or 'maxpool' in user_code.lower() or 'avgpool' in user_code.lower()
            has_linear = 'linear' in user_code.lower()
            
            if not has_conv:
                implementation_warnings.append("      - Conv2d layers not detected")
            if not has_pool:
                implementation_warnings.append("      - Pooling layers not detected")
            if not has_linear:
                implementation_warnings.append("      - Linear (fully connected) layers not detected")
        
        # 6. Validate on hidden test data
        try:
            from unittest.mock import patch
            
            # Load hidden test data marker
            # Check if hidden dataset exists
            hidden_dataset_path = os.path.join(os.path.dirname(__file__), 'hidden_data.pt')
            
            if os.path.exists(hidden_dataset_path):
                # Mock get_dataset_path in the user_module OR patch it globally
                # Since get_dataset_path is imported into user_module, we patch it there
                with patch.object(user_module, 'get_dataset_path') as mocked_get_path:
                    mocked_get_path.return_value = hidden_dataset_path
                    
                    # Run main() again (it will load the hidden dataset)
                    hidden_result = user_module.main()
                    
                    # Check if hidden_result is valid and get metrics
                    error, hidden_metrics = extract_metrics(hidden_result, REQUIRED_METRICS)
                    if error:
                        return f"❌ Hidden Test Case Failed: {error}"
                    
                    # Check thresholds on hidden data (slightly relaxed)
                    if hidden_metrics['accuracy'] < 0.80:
                         return f"❌ Hidden Test Case Failed: Accuracy {hidden_metrics['accuracy']:.4f} is too low on hidden data (expected > 0.80)."
        except Exception as e:
            return f"❌ Hidden Test Case Execution Failed: {str(e)}"

        # 7. Success!
        perf_level = get_performance_level(metrics_dict['accuracy'], PERFORMANCE_THRESHOLDS)
        success_msg = (
            f"✅ Correct! Your CNN model works great!\n"
            f"   📊 Performance Metrics:\n"
            f"      - Accuracy: {metrics_dict['accuracy']:.4f}\n"
            f"      - Macro F1: {metrics_dict['macro_f1']:.4f}\n"
            f"   🎯 {perf_level} performance\n"
        )
        
        if implementation_warnings:
            success_msg += (
                f"\n   ⚠️  Implementation Check - Could not detect:\n" +
                "\n".join(implementation_warnings) + "\n"
                f"   💡 Ensure your CNN has Conv2d, Pooling, and Linear layers"
            )
        else:
            success_msg += f"   🎓 Complete CNN architecture detected!"
        
        return success_msg
    
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"
