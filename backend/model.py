import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# id/constant columns with no signal; dropped so the model can't memorize a row id
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
    """Split into features (X) and target (y), dropping target + id/constant cols."""

    drop = ["Attrition"] + [c for c in ID_AND_CONSTANT_COLS if c in dataframe.columns]

    return dataframe.drop(columns=drop), dataframe["Attrition"]


def train_random_forest(X_train, y_train):
    # class_weight balances the 84/16 split; min_samples_leaf=5 curbs overfitting
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
    # ROC-AUC/recall/precision only; accuracy hidden (majority baseline ~84% flatters)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    return {
        "roc_auc": round(roc_auc_score(y_test, proba), 3),
        "recall": round(recall_score(y_test, pred), 3),
        "precision": round(precision_score(y_test, pred), 3),
    }


@st.cache_resource(show_spinner=False)
def train_workforce_model(dataframe):
    """End-to-end attrition pipeline; cached so page/filter reruns don't retrain."""

    ml_df, encoders = preprocess_workforce_data(dataframe)
    X, y = split_features_target(ml_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = train_random_forest(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)

    return {"model": model, "metrics": metrics, "X": X, "encoders": encoders}


def predict_employee_risk(model, X, encoders, **inputs):
    # score from the median employee + UI overrides; percentile is honest (balanced inflates raw proba)
    row = X.median().round().to_frame().T

    for col, val in inputs.items():
        if col not in X.columns:
            continue
        row[col] = encoders[col].transform([val])[0] if col in encoders else val

    score = model.predict_proba(row[X.columns])[0, 1]
    percentile = (model.predict_proba(X)[:, 1] < score).mean() * 100

    return score, percentile


def simulate_overtime_reduction(model, X, encoders, filtered_df, share):
    # what-if: flip top-risk share% of overtime staff to No, re-score; summed-proba drop = leavers avoided
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