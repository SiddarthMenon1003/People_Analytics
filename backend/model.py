import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Identifier and constant columns carry no predictive signal: EmployeeNumber
# is a row id, and EmployeeCount/Over18/StandardHours are the same value for
# every row. Leaving them in lets the model memorize the id and ranks noise
# as a top driver, so they are dropped before training.
ID_AND_CONSTANT_COLS = ["EmployeeNumber", "EmployeeCount", "Over18", "StandardHours"]


def preprocess_workforce_data(dataframe):
    """Label-encode categorical features for tree-based modeling."""

    ml_df = dataframe.copy()
    categorical_cols = ml_df.select_dtypes(include="object").columns

    encoders = {}

    for col in categorical_cols:
        encoder = LabelEncoder()
        ml_df[col] = encoder.fit_transform(ml_df[col])
        encoders[col] = encoder

    return ml_df, encoders


def split_features_target(dataframe):
    """Split the encoded frame into features (X) and target (y).

    Drops the target plus any identifier/constant columns so the model
    trains only on columns that carry real attrition signal.
    """

    drop = ["Attrition"] + [c for c in ID_AND_CONSTANT_COLS if c in dataframe.columns]

    return dataframe.drop(columns=drop), dataframe["Attrition"]


def train_random_forest(X_train, y_train):
    """Train the Random Forest attrition classifier.

    `class_weight="balanced"` offsets the 84/16 class imbalance so the model
    actually learns to catch leavers instead of predicting "stay" for nearly
    everyone; `min_samples_leaf=5` curbs overfitting on the small dataset.
    """

    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    return model


def evaluate_model(model, X_test, y_test):
    """Held-out ranking and leaver-detection metrics.

    Accuracy is intentionally not reported: on this imbalanced dataset a
    majority-class baseline already scores ~87%, so accuracy flatters a
    model that catches almost no leavers. ROC-AUC, recall, and precision
    describe the model honestly.
    """

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    return {
        "roc_auc": round(roc_auc_score(y_test, proba), 3),
        "recall": round(recall_score(y_test, pred), 3),
        "precision": round(precision_score(y_test, pred), 3),
    }


@st.cache_resource(show_spinner=False)
def train_workforce_model(dataframe):
    """End-to-end workforce attrition model pipeline.

    Cached on the input dataframe's content so switching between dashboard
    pages or filters doesn't retrain the model on every rerun.
    """

    ml_df, encoders = preprocess_workforce_data(dataframe)
    X, y = split_features_target(ml_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = train_random_forest(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)

    return {"model": model, "metrics": metrics, "X": X, "encoders": encoders}


def predict_employee_risk(model, X, encoders, **inputs):
    """Score a single hypothetical employee with the trained model.

    Starts from the median employee (every feature at its dataset median),
    overrides the handful of fields exposed in the UI, and returns the raw
    attrition probability plus the percentile of that probability against
    the whole workforce. Because `class_weight="balanced"` inflates raw
    probabilities, the percentile ("riskier than X% of employees") is the
    honest number to surface rather than the probability on its own.
    """

    row = X.median().round().to_frame().T

    for col, val in inputs.items():
        if col not in X.columns:
            continue
        row[col] = encoders[col].transform([val])[0] if col in encoders else val

    score = model.predict_proba(row[X.columns])[0, 1]
    percentile = (model.predict_proba(X)[:, 1] < score).mean() * 100

    return score, percentile


def simulate_overtime_reduction(model, X, encoders, filtered_df, share):
    """Re-score the workforce after moving `share`% of overtime staff off it.

    A real what-if, not a fixed multiplier: it scores everyone in scope with
    the model, flips the highest-risk `share`% of current overtime workers to
    OverTime="No", re-scores, and reports the change. Because a probability
    sums to an expected headcount, the drop in the summed probability is the
    expected number of leavers avoided — which the cost input turns into a
    savings figure.
    """

    X_scope = X.loc[filtered_df.index]

    if X_scope.empty:
        return {
            "reduction_pct": 0.0,
            "leavers_avoided": 0.0,
            "expected_leavers_before": 0.0,
            "expected_leavers_after": 0.0,
            "moved": 0,
            "overtime_total": 0,
        }

    yes_code = encoders["OverTime"].transform(["Yes"])[0]
    no_code = encoders["OverTime"].transform(["No"])[0]

    before = pd.Series(model.predict_proba(X_scope)[:, 1], index=X_scope.index)
    ot_idx = X_scope.index[X_scope["OverTime"] == yes_code]
    moved = before.loc[ot_idx].nlargest(int(len(ot_idx) * share / 100)).index

    X_sim = X_scope.copy()
    X_sim.loc[moved, "OverTime"] = no_code
    after_total = model.predict_proba(X_sim)[:, 1].sum()
    before_total = before.sum()

    leavers_avoided = before_total - after_total
    reduction_pct = round(leavers_avoided / before_total * 100, 1) if before_total else 0.0

    return {
        "reduction_pct": reduction_pct,
        "leavers_avoided": round(float(leavers_avoided), 1),
        "expected_leavers_before": round(float(before_total), 1),
        "expected_leavers_after": round(float(after_total), 1),
        "moved": int(len(moved)),
        "overtime_total": int(len(ot_idx)),
    }