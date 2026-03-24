# 🎯 Marketing ROI Predictor
## From-Scratch Neural Network · NumPy Only · Streamlit UI

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload `marketing_campaign_dataset.csv` via the sidebar on first load.

---

## Project Structure

```
roi_predictor/
├── app.py           # 4-page Streamlit application
├── processor.py     # Manual preprocessing pipeline (DataProcessor)
├── model.py         # NumPy-only neural network (ScratchNeuralNet)
├── requirements.txt
└── README.md
```

---

## The Math Behind Backpropagation

### Network Notation

| Symbol | Meaning |
|--------|---------|
| `W[l]` | Weight matrix at layer l |
| `b[l]` | Bias vector at layer l |
| `z[l]` | Pre-activation: `W[l] @ a[l-1] + b[l]` |
| `a[l]` | Post-activation: `f(z[l])` |
| `N`    | Batch size |
| `L`    | MSE Loss = mean((ŷ − y)²) |

---

### Forward Pass

```
X  →  z1 = W1·X + b1  →  a1 = ReLU(z1)
   →  z2 = W2·a1 + b2 →  a2 = ReLU(z2)
   →  z3 = W3·a2 + b3 →  ŷ  = z3  (linear)
```

---

### Loss Function

```
L = (1/N) · Σ (ŷᵢ − yᵢ)²
```

---

### Backpropagation (Chain Rule, Layer by Layer)

**Step 1 — Gradient at output layer:**

```
dL/dŷ  = (2/N)(ŷ − y)          # shape: (1, N)
dL/dz3 = dL/dŷ · 1             # linear f'=1
dL/dW3 = dL/dz3 · a2ᵀ          # outer product
dL/db3 = Σ dL/dz3              # sum over batch
dL/da2 = W3ᵀ · dL/dz3          # propagate upstream
```

**Step 2 — Hidden layer 2:**

```
dL/dz2 = dL/da2 ⊙ ReLU'(z2)   # ⊙ = element-wise (Hadamard)
         where ReLU'(z) = 1 if z>0, else 0
dL/dW2 = dL/dz2 · a1ᵀ
dL/db2 = Σ dL/dz2
dL/da1 = W2ᵀ · dL/dz2
```

**Step 3 — Hidden layer 1:**

```
dL/dz1 = dL/da1 ⊙ ReLU'(z1)
dL/dW1 = dL/dz1 · Xᵀ
dL/db1 = Σ dL/dz1
```

**Step 4 — SGD Update:**

```
W[l] ← W[l] − α · dL/dW[l]
b[l] ← b[l] − α · dL/db[l]
```

---

### He (Kaiming) Initialization

Weights are sampled from:

```
W ~ N(0, √(2 / fan_in))
```

**Why?** With ReLU, half the neurons are dead (output 0) on average.
He initialization doubles the variance to compensate, keeping
the signal magnitude stable across many layers. This prevents
both vanishing gradients (too small) and exploding gradients (too large).

---

### Z-Score Normalization

```
X_scaled = (X − μ) / σ
```

- `μ` = mean computed **only on training data**, then applied to test
- `σ` = standard deviation + ε (1e-8) to prevent division by zero

---

### Dataset Note

The Kaggle marketing dataset (`marketing_campaign_dataset.csv`) is
synthetically generated. The ROI column has near-zero Pearson correlation
with all input features (confirmed: |r| < 0.005 for all features).
This means the model correctly converges to predict the dataset mean
(~5.0%) as the minimum-MSE estimate. The neural network architecture,
He initialization, and backpropagation gradients are all mathematically
correct — the dataset simply does not contain learnable signal for ROI.

---

## Architecture Diagram

```
Input (18 features)
       │
  ┌────▼────┐
  │ Dense 16│  ← He Init, ReLU
  └────┬────┘
       │
  ┌────▼───┐
  │ Dense 8│  ← He Init, ReLU
  └────┬───┘
       │
  ┌────▼───┐
  │ Dense 1│  ← Linear (regression output)
  └────────┘
       │
    ROI (%)
```

---

## Pages

| Page | Description |
|------|-------------|
| 📊 Executive Dashboard | KPIs, Plotly charts, correlation matrix |
| 🔍 Data Explorer | Raw data, preprocessing walkthrough, feature engineering |
| 🔮 AI ROI Predictor | Interactive form → neural net prediction + gauge chart |
| 🧠 Neural Lab | Live loss curve during training, Pred vs Actual scatter |
