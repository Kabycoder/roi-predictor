"""
processor.py — Manual Data Preprocessing Pipeline
No scikit-learn. Pure NumPy + Pandas.
All column access is guarded — works with any CSV schema.
"""

import numpy as np
import pandas as pd


class DataProcessor:

    def __init__(self, platform_col="Channel_Used", campaign_col="Campaign_Type"):
        self.platform_col = platform_col
        self.campaign_col = campaign_col
        self.num_means_: dict = {}
        self.num_stds_: dict = {}
        self.platform_categories_: list = []
        self.campaign_categories_: list = []
        self.feature_names_: list = []
        self.is_fitted_: bool = False

    # ── STEP 0: Normalise column names & fill missing columns ──────────
    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = df.columns.str.strip().str.replace(" ", "_")

        # Acquisition_Cost
        if "Acquisition_Cost" not in df.columns:
            for c in df.columns:
                if c.lower().replace(" ", "_") in ["budget","cost","spend","ad_spend"]:
                    df = df.rename(columns={c: "Acquisition_Cost"}); break
        if "Acquisition_Cost" not in df.columns:
            df["Acquisition_Cost"] = 10000.0

        # Channel_Used
        if "Channel_Used" not in df.columns:
            for c in df.columns:
                if c.lower().replace(" ", "_") in ["channel","platform","channel_used"]:
                    df = df.rename(columns={c: "Channel_Used"}); break
        if "Channel_Used" not in df.columns:
            df["Channel_Used"] = "Unknown"

        # Campaign_Type
        if "Campaign_Type" not in df.columns:
            for c in df.columns:
                if c.lower().replace(" ", "_") in ["campaign","type","campaign_type"]:
                    df = df.rename(columns={c: "Campaign_Type"}); break
        if "Campaign_Type" not in df.columns:
            df["Campaign_Type"] = "General"

        # Helper columns with safe defaults
        defaults = {"Clicks": 500, "Impressions": 5000,
                    "Engagement_Score": 5, "Conversion_Rate": 0.08, "ROI": 5.0}
        for col, val in defaults.items():
            if col not in df.columns:
                df[col] = float(val)

        return df

    # ── STEP 1: Clean ──────────────────────────────────────────────────
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._normalise(df)

        # Parse Acquisition_Cost string → float
        if not pd.api.types.is_numeric_dtype(df["Acquisition_Cost"]):
            df["Acquisition_Cost"] = (
                df["Acquisition_Cost"].astype(str)
                .str.replace(r"[\$,]", "", regex=True).astype(float)
            )

        # Drop non-numeric string/date columns that can't be features
        always_drop = ["Date", "Company", "Target_Audience", "Duration",
                       "Location", "Language", "Customer_Segment", "Campaign_ID"]
        df = df.drop(columns=[c for c in always_drop if c in df.columns])

        # Impute remaining nulls: numeric → mean, categorical → mode
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].mean())
        for col in df.select_dtypes(include=["object","string"]).columns:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].mode()[0])

        return df

    # ── STEP 2: Feature Engineering ───────────────────────────────────
    @staticmethod
    def _engineer(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Ensure numeric before log
        if not pd.api.types.is_numeric_dtype(df["Acquisition_Cost"]):
            df["Acquisition_Cost"] = (
                df["Acquisition_Cost"].astype(str)
                .str.replace(r"[\$,]", "", regex=True).astype(float)
            )
        df["Log_Spend"]       = np.log1p(df["Acquisition_Cost"])
        df["Spend_per_Click"] = df["Acquisition_Cost"] / df["Clicks"].replace(0, 1)
        df["CTR"]             = df["Clicks"] / df["Impressions"].replace(0, 1)
        return df

    # ── STEP 3: One-Hot Encoding (manual) ─────────────────────────────
    def _ohe(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        df = df.copy()

        def encode(col, cats):
            if col not in df.columns:
                for c in cats:
                    df[f"{col}_{c}"] = 0.0
                return df
            s = df[col].astype(str)
            for c in cats:
                df[f"{col}_{c}"] = (s == c).astype(float)
            return df.drop(columns=[col])

        if fit:
            self.platform_categories_ = (
                sorted(df[self.platform_col].astype(str).unique().tolist())
                if self.platform_col in df.columns else ["Unknown"]
            )
            self.campaign_categories_ = (
                sorted(df[self.campaign_col].astype(str).unique().tolist())
                if self.campaign_col in df.columns else ["General"]
            )

        df = encode(self.platform_col, self.platform_categories_)
        df = encode(self.campaign_col,  self.campaign_categories_)
        return df

    # ── STEP 4: Z-Score Normalisation ────────────────────────────────
    def _zfit(self, X, names):
        self.num_means_ = {n: float(X[:, i].mean()) for i, n in enumerate(names)}
        self.num_stds_  = {n: float(X[:, i].std()) + 1e-8 for i, n in enumerate(names)}

    def _ztransform(self, X, names):
        mu  = np.array([self.num_means_[n] for n in names])
        sig = np.array([self.num_stds_[n]  for n in names])
        return (X - mu) / sig

    # ── STEP 5: Train/Test Split ──────────────────────────────────────
    @staticmethod
    def _split(X, y, ratio=0.2, seed=42):
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(X))
        n   = int(len(idx) * (1 - ratio))
        return X[idx[:n]], X[idx[n:]], y[idx[:n]], y[idx[n:]]

    # ── PUBLIC: fit_transform ─────────────────────────────────────────
    def fit_transform(self, df: pd.DataFrame):
        df = self._clean(df)
        df = self._engineer(df)
        df = self._ohe(df, fit=True)

        # Drop any remaining non-numeric columns (safety net)
        for col in df.columns.tolist():
            if df[col].dtype == object or str(df[col].dtype) == "string":
                df = df.drop(columns=[col])

        if "ROI" not in df.columns:
            raise ValueError("ROI column not found after preprocessing.")

        y    = df["ROI"].values.astype(float)
        X_df = df.drop(columns=["ROI"])

        self.feature_names_ = list(X_df.columns)
        X = X_df.values.astype(float)

        X_tr, X_te, y_tr, y_te = self._split(X, y)
        self._zfit(X_tr, self.feature_names_)
        self.is_fitted_ = True

        return (self._ztransform(X_tr, self.feature_names_),
                self._ztransform(X_te, self.feature_names_),
                y_tr, y_te)

    # ── PUBLIC: transform_single (prediction form) ────────────────────
    def transform_single(self, raw: dict) -> np.ndarray:
        if not self.is_fitted_:
            raise RuntimeError("Call fit_transform first.")

        row = pd.DataFrame([raw])

        # Parse cost
        if "Acquisition_Cost" in row.columns and not pd.api.types.is_numeric_dtype(row["Acquisition_Cost"]):
            row["Acquisition_Cost"] = (
                row["Acquisition_Cost"].astype(str)
                .str.replace(r"[\$,]", "", regex=True).astype(float)
            )

        # Engineered features
        ac  = float(row.get("Acquisition_Cost", pd.Series([10000])).iloc[0])
        cl  = float(row.get("Clicks",           pd.Series([500])).iloc[0])
        imp = float(row.get("Impressions",       pd.Series([5000])).iloc[0])
        row["Log_Spend"]       = np.log1p(ac)
        row["Spend_per_Click"] = ac / max(cl, 1)
        row["CTR"]             = cl / max(imp, 1)

        # One-hot encode
        pval = str(row[self.platform_col].iloc[0]) if self.platform_col in row.columns else ""
        cval = str(row[self.campaign_col].iloc[0])  if self.campaign_col  in row.columns else ""
        for cat in self.platform_categories_:
            row[f"{self.platform_col}_{cat}"] = float(pval == cat)
        for cat in self.campaign_categories_:
            row[f"{self.campaign_col}_{cat}"]  = float(cval == cat)

        # Drop non-feature columns
        drop = [self.platform_col, self.campaign_col,
                "Campaign_ID","Company","Target_Audience","Duration",
                "Location","Language","Customer_Segment","Date",
                "Conversion_Rate","ROI"]
        row = row.drop(columns=[c for c in drop if c in row.columns])

        # Align to training layout
        for col in self.feature_names_:
            if col not in row.columns:
                row[col] = 0.0
        row = row[self.feature_names_]

        return self._ztransform(row.values.astype(float), self.feature_names_)
