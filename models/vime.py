import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from models.basemodel import BaseModel
from utils.io_utils import get_output_path


class VIME(BaseModel):

    def __init__(self, params, args):
        super().__init__(params, args)

        self.batch_size = 128

        self.device = torch.device('cuda' if args.use_gpu and torch.cuda.is_available() else 'cpu')
        print("On Device:", self.device)

        self.model_self = VIMESelf(args.num_features).to(self.device)
        self.model_semi = VIMESemi(args, args.num_features, args.num_classes).to(self.device)

    def fit(self, X, y, X_val=None, y_val=None):
        # For some reason this has to be set explicitly to work with categorical data
        X = np.array(X, dtype=np.float)
        X_val = np.array(X_val, dtype=np.float)

        X_unlab = np.concatenate([X, X_val], axis=0)

        self.fit_self(X_unlab, p_m=self.params["p_m"], alpha=self.params["alpha"])
        self.fit_semi(X, y, X, X_val, y_val, p_m=self.params["p_m"], K=self.params["K"], beta=self.params["beta"])

    def predict(self, X):
        self.load_model(filename_extension="best", directory="tmp")
        self.model_self.eval()
        self.model_semi.eval()

        # For some reason this has to be set explicitly to work with categorical data
        X = np.array(X, dtype=np.float)
        X = torch.tensor(X).float()

        test_dataset = TensorDataset(X)
        test_loader = DataLoader(dataset=test_dataset, batch_size=128, shuffle=True, num_workers=2)

        self.predictions = []

        with torch.no_grad():
            for batch_X in test_loader:
                X_encoded = torch.sigmoid(self.model_self.input_layer(batch_X[0].to(self.device)))
                preds = self.model_semi(X_encoded)
                self.predictions.append(preds)

        self.predictions = np.concatenate(self.predictions)
        return self.predictions

    def fit_self(self, X, p_m=0.3, alpha=2):
        optimizer = optim.RMSprop(self.model_self.parameters(), lr=0.001)
        loss_func_mask = nn.BCELoss()
        loss_func_feat = nn.MSELoss()

        m_unlab = mask_generator(p_m, X)
        m_label, x_tilde = pretext_generator(m_unlab, X)

        x_tilde = torch.tensor(x_tilde).float()
        m_label = torch.tensor(m_label).float()
        X = torch.tensor(X).float()
        train_dataset = TensorDataset(x_tilde, m_label, X)
        train_loader = DataLoader(dataset=train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=2)

        for epoch in range(10):
            for batch_X, batch_mask, batch_feat in train_loader:
                out_mask, out_feat = self.model_self(batch_X.to(self.device))

                loss_mask = loss_func_mask(out_mask, batch_mask.to(self.device))
                loss_feat = loss_func_feat(out_feat, batch_feat.to(self.device))

                loss = loss_mask + loss_feat * alpha

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

    def fit_semi(self, X, y, x_unlab, X_val=None, y_val=None, p_m=0.3, K=3, beta=1):

        X = torch.tensor(X).float()
        y = torch.tensor(y)
        x_unlab = torch.tensor(x_unlab).float()

        X_val = torch.tensor(X_val).float()
        y_val = torch.tensor(y_val)

        if self.args.objective == "regression":
            loss_func_supervised = nn.MSELoss()
            y = y.float()
            y_val = y_val.float()
        elif self.args.objective == "classification":
            loss_func_supervised = nn.CrossEntropyLoss()
        elif self.args.objective == "binary_classification":
            loss_func_supervised = nn.BCEWithLogitsLoss()
            y = y.float()
            y_val = y_val.float()

        optimizer = optim.AdamW(self.model_semi.parameters())

        train_dataset = TensorDataset(X, y, x_unlab)
        train_loader = DataLoader(dataset=train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=2,
                                  drop_last=True)

        val_dataset = TensorDataset(X_val, y_val)
        val_loader = DataLoader(dataset=val_dataset, batch_size=self.batch_size, shuffle=True)

        val_dim = y_val.shape[0]
        min_val_loss = float("inf")
        min_val_loss_idx = 0

        for epoch in range(1000):
            for i, (batch_X, batch_y, batch_unlab) in enumerate(train_loader):

                batch_X_encoded = self.model_self.input_layer(batch_X.to(self.device))
                y_hat = self.model_semi(batch_X_encoded)

                yv_hats = torch.empty(K, self.batch_size, self.args.num_classes)
                for rep in range(K):
                    m_batch = mask_generator(p_m, batch_unlab)
                    _, batch_unlab_tmp = pretext_generator(m_batch, batch_unlab)

                    batch_unlab_encoded = self.model_self.input_layer(batch_unlab_tmp.float().to(self.device))
                    yv_hat = self.model_semi(batch_unlab_encoded)
                    yv_hats[rep] = yv_hat

                if self.args.objective == "regression" or self.args.objective == "binary_classification":
                    y_hat = y_hat.squeeze()

                y_loss = loss_func_supervised(y_hat, batch_y.to(self.device))
                yu_loss = torch.mean(torch.var(yv_hats, dim=0))
                loss = y_loss + beta * yu_loss

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Early Stopping
                val_loss = 0.0
                for val_i, (batch_val_X, batch_val_y) in enumerate(val_loader):
                    batch_val_X_encoded = self.model_self.input_layer(batch_val_X.to(self.device))
                    y_hat = self.model_semi(batch_val_X_encoded)

                    if self.args.objective == "regression" or self.args.objective == "binary_classification":
                        y_hat = y_hat.squeeze()

                    val_loss += loss_func_supervised(y_hat, batch_val_y.to(self.device))

                val_loss /= val_dim

                current_idx = (i + 1) * (epoch + 1)

                if val_loss < min_val_loss:
                    min_val_loss = val_loss
                    min_val_loss_idx = current_idx

                    self.save_model(filename_extension="best", directory="tmp")

                if min_val_loss_idx + self.args.early_stopping_rounds < current_idx:
                    print("Early stopping applies.", i)
                    return

    def save_model(self, filename_extension="", directory="models"):
        filename_self = get_output_path(self.args, directory=directory, filename="m_self", extension=filename_extension,
                                        file_type="pt")
        torch.save(self.model_self.state_dict(), filename_self)

        filename_semi = get_output_path(self.args, directory=directory, filename="m_semi", extension=filename_extension,
                                        file_type="pt")
        torch.save(self.model_semi.state_dict(), filename_semi)

    def load_model(self, filename_extension="", directory="models"):
        filename_self = get_output_path(self.args, directory=directory, filename="m_self", extension=filename_extension,
                                        file_type="pt")
        state_dict = torch.load(filename_self)
        self.model_self.load_state_dict(state_dict)

        filename_semi = get_output_path(self.args, directory=directory, filename="m_semi", extension=filename_extension,
                                        file_type="pt")
        state_dict = torch.load(filename_semi)
        self.model_semi.load_state_dict(state_dict)

    @classmethod
    def define_trial_parameters(cls, trial, args):
        params = {
            "p_m": trial.suggest_float("p_m", 0.1, 0.9),
            "alpha": trial.suggest_float("alpha", 0.1, 10),
            "K": trial.suggest_categorical("K", [2, 3, 5, 10, 15, 20]),
            "beta": trial.suggest_float("beta", 0.1, 10)
        }
        return params


class VIMESelf(nn.Module):

    def __init__(self, input_dim):
        super().__init__()

        self.input_layer = nn.Linear(input_dim, input_dim)

        self.mask_layer = nn.Linear(input_dim, input_dim)
        self.feat_layer = nn.Linear(input_dim, input_dim)

    def forward(self, x):
        x = F.relu(self.input_layer(x))

        out_mask = torch.sigmoid(self.mask_layer(x))
        out_feat = torch.sigmoid(self.feat_layer(x))

        return out_mask, out_feat


class VIMESemi(nn.Module):

    def __init__(self, args, input_dim, output_dim, hidden_dim=100, n_layers=5):
        super().__init__()
        self.args = args

        self.input_layer = nn.Linear(input_dim, hidden_dim)

        self.layers = nn.ModuleList()
        self.layers.extend([nn.Linear(hidden_dim, hidden_dim) for _ in range(n_layers - 1)])

        self.output_layer = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = F.relu(self.input_layer(x))

        for layer in self.layers:
            x = F.relu(layer(x))

        out = self.output_layer(x)

        if self.args.objective == "classification":
            out = F.softmax(out, dim=1)

        return out


'''
    VIME code copied from: https://github.com/jsyoon0823/VIME
'''


def mask_generator(p_m, x):
    mask = np.random.binomial(1, p_m, x.shape)
    return mask


def pretext_generator(m, x):
    # Parameters
    no, dim = x.shape
    # Randomly (and column-wise) shuffle data
    x_bar = np.zeros([no, dim])
    for i in range(dim):
        idx = np.random.permutation(no)
        x_bar[:, i] = x[idx, i]

    # Corrupt samples
    x_tilde = x * (1 - m) + x_bar * m
    # Define new mask matrix
    m_new = 1 * (x != x_tilde)

    return m_new, x_tilde
