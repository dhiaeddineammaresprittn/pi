import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import pickle
import os

# Charger tous les modèles
import torch.nn as nn

# === CLASSIFICATION ===

class SectorClassifier(nn.Module):
    def __init__(self, input_dim=768, hidden_dim=512, output_dim=83):
        super(SectorClassifier, self).__init__()
        self.lstm = nn.LSTM(input_size=input_dim, hidden_size=hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = x.unsqueeze(1)  # Ajoute une dimension pour LSTM
        out, (h_n, c_n) = self.lstm(x)
        return self.fc(h_n[-1])


# === SCORE ===
class EmployabilityRegressor(nn.Module):
    def __init__(self, input_dim=384):
        super(EmployabilityRegressor, self).__init__()
        self.fc1 = nn.Linear(input_dim, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

def load_models():
    # 1. Créer la structure vide
    sector_model = SectorClassifier()
    score_model = EmployabilityScorer()
    score_model.load_state_dict(torch.load("models/employability_model.pt", map_location='cpu'))
    score_model.eval()


    # 2. Charger les poids
    sector_model.load_state_dict(torch.load("models/career_sector_model.pt", map_location='cpu'))
    sector_model.eval()

    score_model.load_state_dict(torch.load("models/employability_model.pt", map_location='cpu'))
    score_model.eval()

    # 3. Charger Sentence-BERT et l’encoder
    sentence_model = SentenceTransformer("all-mpnet-base-v2")


    with open("models/label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)

    return sector_model, score_model, sentence_model, label_encoder

# Prédiction secteurs
def predict_sectors(text, sector_model, sentence_model, label_encoder):
    embedding = sentence_model.encode([text])
    output = sector_model(torch.tensor(embedding, dtype=torch.float))
    probs = F.softmax(output, dim=1).detach().numpy()[0]
    top3_idx = probs.argsort()[-3:][::-1]
    return [(label_encoder.inverse_transform([i])[0], round(probs[i]*100, 2)) for i in top3_idx]

# Prédiction score employabilité
def predict_score(text, score_model, sentence_model):
    embedding = sentence_model.encode([text])
    score = score_model(torch.tensor(embedding, dtype=torch.float)).item()
    return round(score, 2)
class EmployabilityScorer(nn.Module):
    def __init__(self, input_dim=768, hidden_dim=256):
        super(EmployabilityScorer, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
