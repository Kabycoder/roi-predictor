"""
model.py — From-Scratch Neural Network (NumPy only)
Architecture: Input → Dense(16, ReLU) → Dense(8, ReLU) → Dense(1, Linear)
Training:     He Initialization, MSE Loss, Backprop, Mini-batch GD
"""

import numpy as np


# ──────────────────────────────────────────────────────────────────────
# ACTIVATION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def relu(z: np.ndarray) -> np.ndarray:
    """ReLU: max(0, z)  — introduces non-linearity in hidden layers."""
    return np.maximum(0.0, z)


def relu_derivative(z: np.ndarray) -> np.ndarray:
    """
    d/dz ReLU(z) = 1 if z > 0, else 0.
    Used during backprop to pass gradients only through active neurons.
    """
    return (z > 0).astype(float)


def linear(z: np.ndarray) -> np.ndarray:
    """Identity activation for the output layer (regression task)."""
    return z


def linear_derivative(z: np.ndarray) -> np.ndarray:
    return np.ones_like(z)


# ──────────────────────────────────────────────────────────────────────
# NEURAL NETWORK CLASS
# ──────────────────────────────────────────────────────────────────────

class ScratchNeuralNet:
    """
    Fully-connected feedforward network built with NumPy.

    Layers
    ------
    0 → input (n_features)
    1 → hidden, 16 neurons, ReLU
    2 → hidden,  8 neurons, ReLU
    3 → output,  1 neuron,  Linear

    Weight Initialization: He (Kaiming)
    ────────────────────────────────────
    W ~ N(0, sqrt(2 / fan_in))
    This keeps the variance of activations roughly constant across layers
    when ReLU is used, preventing vanishing/exploding gradients.

    Backpropagation — Chain Rule Derivation
    ────────────────────────────────────────
    Let:
        L     = MSE = mean((ŷ - y)²)
        z[l]  = W[l] @ a[l-1] + b[l]   (pre-activation)
        a[l]  = f(z[l])                 (post-activation)
        a[0]  = X (input)
        a[L]  = ŷ (output)

    Output layer (linear activation):
        dL/dŷ  = 2(ŷ - y) / N           ← MSE gradient
        dL/dz3 = dL/dŷ · f'(z3) = dL/dŷ  (f' = 1 for linear)
        dL/dW3 = dL/dz3 @ a2.T
        dL/db3 = sum(dL/dz3, axis=1)
        dL/da2 = W3.T @ dL/dz3           ← propagate back to layer 2

    Hidden layer l (ReLU):
        dL/dz[l] = dL/da[l] * ReLU'(z[l])   ← Hadamard product (element-wise)
        dL/dW[l] = dL/dz[l] @ a[l-1].T
        dL/db[l] = sum(dL/dz[l], axis=1)
        dL/da[l-1] = W[l].T @ dL/dz[l]      ← continue backprop

    Parameter update (SGD):
        W[l] ← W[l] - lr · dL/dW[l]
        b[l] ← b[l] - lr · dL/db[l]
    """

    def __init__(self, n_features: int, lr: float = 0.001, seed: int = 42):
        self.lr = lr
        self.n_features = n_features
        rng = np.random.default_rng(seed)

        # ── He Initialization ──────────────────────────────────────
        # fan_in for each layer: previous layer size
        def he(fan_in, fan_out):
            std = np.sqrt(2.0 / fan_in)
            return rng.normal(0, std, (fan_out, fan_in))

        self.W = [
            he(n_features, 16),  # Layer 1: (16, n_features)
            he(16, 8),           # Layer 2: (8, 16)
            he(8, 1),            # Layer 3: (1, 8)
        ]
        self.b = [
            np.zeros((16, 1)),
            np.zeros((8, 1)),
            np.zeros((1, 1)),
        ]

        self.loss_history: list[float] = []
        self.val_loss_history: list[float] = []

    # ── FORWARD PASS ───────────────────────────────────────────────
    def forward(self, X: np.ndarray):
        """
        X shape: (n_samples, n_features) → transposed internally to (n_features, n_samples)
        Returns predictions (n_samples,) and cache for backprop.
        """
        A = X.T  # (n_features, n_samples)
        cache = {"A0": A}

        # Hidden layer 1
        Z1 = self.W[0] @ A + self.b[0]
        A1 = relu(Z1)
        cache["Z1"], cache["A1"] = Z1, A1

        # Hidden layer 2
        Z2 = self.W[1] @ A1 + self.b[1]
        A2 = relu(Z2)
        cache["Z2"], cache["A2"] = Z2, A2

        # Output layer (linear)
        Z3 = self.W[2] @ A2 + self.b[2]
        A3 = linear(Z3)
        cache["Z3"], cache["A3"] = Z3, A3

        return A3.ravel(), cache

    # ── LOSS ────────────────────────────────────────────────────────
    @staticmethod
    def mse(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        return float(np.mean((y_pred - y_true) ** 2))

    # ── BACKPROPAGATION ─────────────────────────────────────────────
    def backward(self, y_pred: np.ndarray, y_true: np.ndarray, cache: dict):
        """
        Implements the chain rule end-to-end.
        Returns gradient dicts for W and b at each layer.
        """
        N = len(y_true)

        # ── Output layer ──
        # dL/dA3: gradient of MSE w.r.t. predictions → shape (1, N)
        dA3 = (2.0 / N) * (y_pred - y_true).reshape(1, -1)

        # linear derivative = 1, so dZ3 = dA3
        dZ3 = dA3 * linear_derivative(cache["Z3"])          # (1, N)
        dW3 = dZ3 @ cache["A2"].T                           # (1, 8)
        db3 = dZ3.sum(axis=1, keepdims=True)                # (1, 1)
        dA2 = self.W[2].T @ dZ3                             # (8, N)

        # ── Hidden layer 2 ──
        dZ2 = dA2 * relu_derivative(cache["Z2"])            # (8, N)
        dW2 = dZ2 @ cache["A1"].T                           # (8, 16)
        db2 = dZ2.sum(axis=1, keepdims=True)                # (8, 1)
        dA1 = self.W[1].T @ dZ2                             # (16, N)

        # ── Hidden layer 1 ──
        dZ1 = dA1 * relu_derivative(cache["Z1"])            # (16, N)
        dW1 = dZ1 @ cache["A0"].T                           # (16, n_features)
        db1 = dZ1.sum(axis=1, keepdims=True)                # (16, 1)

        return [dW1, dW2, dW3], [db1, db2, db3]

    # ── PARAMETER UPDATE ────────────────────────────────────────────
    def _update(self, grads_W, grads_b):
        for l in range(3):
            self.W[l] -= self.lr * grads_W[l]
            self.b[l] -= self.lr * grads_b[l]

    # ── TRAINING LOOP ───────────────────────────────────────────────
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 100,
        batch_size: int = 256,
        progress_callback=None,
    ) -> list[float]:
        """
        Mini-batch gradient descent.

        progress_callback(epoch, train_loss, val_loss) is called after each epoch
        so Streamlit can stream updates to the UI.
        """
        self.loss_history = []
        self.val_loss_history = []
        n = len(X_train)
        rng = np.random.default_rng(0)

        for epoch in range(1, epochs + 1):
            # Shuffle training set each epoch
            idx = rng.permutation(n)
            X_shuf, y_shuf = X_train[idx], y_train[idx]

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n, batch_size):
                Xb = X_shuf[start: start + batch_size]
                yb = y_shuf[start: start + batch_size]

                y_pred, cache = self.forward(Xb)
                batch_loss = self.mse(y_pred, yb)
                epoch_loss += batch_loss
                n_batches += 1

                grads_W, grads_b = self.backward(y_pred, yb, cache)
                self._update(grads_W, grads_b)

            train_loss = epoch_loss / n_batches
            val_pred, _ = self.forward(X_val)
            val_loss = self.mse(val_pred, y_val)

            self.loss_history.append(train_loss)
            self.val_loss_history.append(val_loss)

            if progress_callback:
                progress_callback(epoch, train_loss, val_loss)

        return self.loss_history

    # ── INFERENCE ───────────────────────────────────────────────────
    def predict(self, X: np.ndarray) -> np.ndarray:
        preds, _ = self.forward(X)
        return preds

    # ── METRICS ─────────────────────────────────────────────────────
    @staticmethod
    def r2_score(y_true, y_pred) -> float:
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return float(1 - ss_res / (ss_tot + 1e-10))

    @staticmethod
    def mae(y_true, y_pred) -> float:
        return float(np.mean(np.abs(y_true - y_pred)))

    def get_weights_summary(self) -> dict:
        return {
            f"W{i+1}_shape": self.W[i].shape for i in range(3)
        }
