# People Analytics

Predicting employee attrition and turning it into workforce decisions, served as a
multi-page Streamlit dashboard.

**▶ Launch the live app:** **https://workforce-intelligence-platform.onrender.com**

_Hosted on Render — the first load may take ~30s while the free instance wakes._

Built on the IBM HR Analytics Employee Attrition dataset (1,470 employees, 16.1%
attrition).

---

## What it does

The app loads the HR dataset (or a CSV you upload), trains an attrition model, and
presents four pages:

1. **Overview** — headline KPIs (workforce size, attrition rate, high-risk share),
   the organization-wide risk verdict, and honest model metrics (ROC-AUC and the
   share of leavers the model catches).
2. **Workforce Analytics** — overtime and burnout cuts, satisfaction / work-life /
   tenure / income breakdowns, and department distribution, with narratives computed
   from the data (not fixed text).
3. **Risk Intelligence** — per-employee risk scoring, a risk heatmap, and a
   model-based what-if: move a chosen share of overtime employees (highest-risk
   first) off overtime and see the predicted change.
4. **Strategic Insights** — a workforce health index, the model's attrition drivers,
   a live single-employee predictor, and an impact simulation that converts avoided
   leavers into a cost estimate.

Every page reads its risk verdict from one function, so the pages agree with each
other.

---

## The model

The deployed app trains a **Random Forest** (`class_weight="balanced"`, identifier
and constant columns dropped, stratified split) on each run and caches it.

Honest held-out metrics on this dataset:

| Metric | Value | Note |
|---|---|---|
| ROC-AUC | ~0.79 | ranking quality |
| Recall (leavers) | ~0.36 | share of actual leavers caught |
| Precision | ~0.49 | |
| Accuracy | ~0.83 | a majority-class baseline already scores ~0.84 |

Accuracy is deliberately **not** used as the headline: on a dataset this imbalanced a
model that predicts "stays" for almost everyone scores ~84% while catching no
leavers. ROC-AUC and recall describe the model honestly.

Recall is modest by design: the product value is the risk **ranking** (who to
prioritise) and the cost simulation, not flagging every leaver — pushing recall up
would trade away the precision the cost model relies on.

The development notebook (`development/`) compares Logistic Regression, Random Forest,
and Gradient Boosting. Logistic Regression scores the best ROC-AUC (~0.82) and gives
the most interpretable coefficients; the app keeps the Random Forest for its feature
importances. All three land in the 0.77–0.82 test ROC-AUC range once the data leak
(see below) is fixed.

### Assumptions

The dollar figures (cost exposure, projected savings) are driven by a
**"Replacement cost per leaver"** input in the sidebar (default $15,000). It is an
editable assumption, not a hidden constant — change it and every dollar figure
updates.

---

## Project structure

```
.
├── app.py                     # Streamlit entry point (load, validate, train, route)
├── requirements.txt           # Deployed-app dependencies (pinned)
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
├── backend/                   # Pure logic, no Streamlit
│   ├── model.py               #   training, single-employee prediction, overtime sim
│   ├── analytics.py           #   KPI/aggregation calculations, org risk verdict
│   ├── risk_engine.py         #   per-employee risk scoring and classification
│   └── insights_engine.py     #   data-driven narrative text
├── frontend/                  # Layout only
│   ├── overview.py
│   ├── workforce_analytics.py
│   ├── risk_intelligence.py
│   ├── strategic_insights.py
│   ├── sidebar.py
│   ├── components.py          #   reusable UI building blocks
│   ├── styles.py
│   └── theme.py
└── development/
    ├── Workforce Intelligence Analysis.ipynb   # EDA + model comparison
    └── requirements.txt       # notebook-only extras (jupyter, matplotlib, seaborn)
```

---

## Running locally

```bash
# from the repo root, in a Python 3 environment
pip install -r requirements.txt
streamlit run app.py
```

For the analysis notebook:

```bash
pip install -r development/requirements.txt
jupyter lab
```

---

## A note on the notebook

The notebook had **two** leakage bugs, both fixed:

1. **Upsampling before the split.** An earlier version upsampled the minority class
   before the train/test split, so copies of the same employees landed in both the
   training and test sets and inflated the scores (RF test ROC-AUC ~0.99). The split
   now happens first and only the training set is upsampled.
2. **Upsampling before cross-validation.** `GridSearchCV` then ran on the already
   upsampled training set, so duplicated minority rows spanned the CV folds and
   inflated `best_score_` the same way. Each grid now uses an `imblearn` pipeline
   (`RandomOverSampler` → estimator) so the resampling happens **inside** every fold.
   The honest leak-free CV ROC-AUCs are LR ~0.84, RF ~0.81, GB ~0.81, in line with the
   held-out test numbers above.

---

## Author

Siddarth Menon — Master's student, Data Science & AI Strategy, emlyon business school.
