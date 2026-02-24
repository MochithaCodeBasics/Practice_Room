import os
import math
import numpy as np
import pandas as pd


def _mae(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def validate(user_module):
    try:
        if not hasattr(user_module, "predict_stock"):
            return "❌ Function `predict_stock(X, y)` is not defined."

        func = user_module.predict_stock
        if not callable(func):
            return "❌ `predict_stock` is not callable."

        # Public deterministic regression test
        X_public = np.array([[1.0], [2.0], [3.0], [4.0]])
        y_public = np.array([2.0, 4.0, 6.0, 8.0])
        model = func(X_public, y_public)

        if not hasattr(model, "predict"):
            return "❌ Expected a fitted model object with a `.predict()` method."

        preds_public = np.asarray(model.predict(np.array([[5.0], [6.0]])), dtype=float)
        if preds_public.shape != (2,):
            return f"❌ Public test: prediction shape mismatch. Expected (2,), got {preds_public.shape}."

        if not np.allclose(preds_public, np.array([10.0, 12.0]), atol=1e-2):
            return f"❌ Public test: incorrect predictions. Got {preds_public.tolist()}."

        # Hidden file-based metric test
        base = os.path.dirname(__file__)
        train_df = pd.read_csv(os.path.join(base, "stocks.csv"))
        hidden_df = pd.read_csv(os.path.join(base, "hidden_test_data.csv"))

        if "price" not in train_df.columns or "price" not in hidden_df.columns:
            return "❌ Expected `price` column in both public and hidden stock datasets."

        # Use sequential index as feature to form a time-step regression baseline.
        X_train = np.arange(len(train_df), dtype=float).reshape(-1, 1)
        y_train = train_df["price"].to_numpy(dtype=float)
        X_hidden = np.arange(len(train_df), len(train_df) + len(hidden_df), dtype=float).reshape(-1, 1)
        y_hidden = hidden_df["price"].to_numpy(dtype=float)

        model_hidden = func(X_train, y_train)
        if not hasattr(model_hidden, "predict"):
            return "❌ Hidden test: returned object must support `.predict()`."

        preds_hidden = np.asarray(model_hidden.predict(X_hidden), dtype=float)
        if preds_hidden.shape != (len(hidden_df),):
            return "❌ Hidden test: prediction length mismatch."

        hidden_mae = _mae(y_hidden, preds_hidden)
        if hidden_mae > 1.0:
            return f"❌ Hidden test: MAE too high on hidden stock data ({hidden_mae:.4f})."

        # Additional seeded hidden metric check (generalization on synthetic linear data)
        rng = np.random.default_rng(2026)
        X_syn = rng.normal(size=(40, 2))
        y_syn = 3.5 * X_syn[:, 0] - 1.25 * X_syn[:, 1] + 7.0
        X_syn_test = rng.normal(size=(10, 2))
        y_syn_test = 3.5 * X_syn_test[:, 0] - 1.25 * X_syn_test[:, 1] + 7.0

        model_syn = func(X_syn, y_syn)
        preds_syn = np.asarray(model_syn.predict(X_syn_test), dtype=float)
        syn_mae = _mae(y_syn_test, preds_syn)
        if syn_mae > 1e-3:
            return f"❌ Hidden test: synthetic linear-data MAE too high ({syn_mae:.6f})."

        return "✅ Correct! All test cases passed successfully."
    except Exception as e:
        return f"⚠️ Validation error: {e}"
