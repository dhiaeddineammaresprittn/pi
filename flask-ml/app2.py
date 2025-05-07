from flask import Flask, render_template_string
import pandas as pd
import pyodbc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import numpy as np

app = Flask(__name__)

def load_and_process_data():
    conn_str = (
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=DESKTOP-BJ2KL4N\DHIAEDDINE;"
        r"DATABASE=DW_Admission;"
        r"Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str)

    query = """
    SELECT id_concours, date_enreg, date_convocation, date_entretien,
           date_resultat, date_preinscrits, id_et, score_final, resultat, id_candidature
    FROM dbo.Dim_Candidature
    """
    df = pd.read_sql(query, conn)

    date_cols = ['date_enreg', 'date_convocation', 'date_entretien', 'date_resultat', 'date_preinscrits']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df.dropna(subset=['score_final', 'date_enreg', 'date_entretien', 'resultat'], inplace=True)
    df['days_to_interview'] = (df['date_entretien'] - df['date_enreg']).dt.days

    le = LabelEncoder()
    df['resultat_encoded'] = le.fit_transform(df['resultat'])

    return df, le

@app.route('/')
def detect_frauds():
    df, le = load_and_process_data()

    X = df[['score_final', 'days_to_interview']]
    y = df['resultat_encoded']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    df['predicted_result'] = model.predict(X)
    df['is_suspect'] = df['resultat_encoded'] != df['predicted_result']
    df['predicted_label'] = le.inverse_transform(df['predicted_result'])
    df['actual_label'] = df['resultat']

    suspected_frauds = df[df['is_suspect']][[
        'id_et', 'score_final', 'days_to_interview', 'actual_label', 'predicted_label'
    ]].head(20).to_dict(orient='records')

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Détection de Fraude</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            table {
                width: 100%;
                margin-top: 20px;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .statistics {
                margin-top: 30px;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
            }
            .statistics h3 {
                margin-top: 0;
            }
        </style>
    </head>
    <body>
        <h1>Résultats de la Détection des fautes</h1>

        <h2>Top 20 des Candidats Suspects des fautes</h2>
        <table>
            <thead>
                <tr>
                    <th>ID Candidat</th>
                    <th>Score Final</th>
                    <th>Délai Entretien (Jours)</th>
                    <th>Résultat Actuel</th>
                    <th>Résultat Prédit</th>
                </tr>
            </thead>
            <tbody>
    """
    for fraud in suspected_frauds:
        html += f"""
        <tr>
            <td>{fraud['id_et']}</td>
            <td>{fraud['score_final']}</td>
            <td>{fraud['days_to_interview']}</td>
            <td>{fraud['actual_label']}</td>
            <td>{fraud['predicted_label']}</td>
        </tr>
        """
    html += """
            </tbody>
        </table>

        <div class="statistics">
            <h3>Statistiques du Modèle</h3>
            <p><strong>Erreur Absolue Moyenne (MAE):</strong> {{ mae }}</p>
            <p><strong>Erreur Quadratique Moyenne (RMSE):</strong> {{ rmse }}</p>
            <p><strong>Coefficient de Détermination (R²):</strong> {{ r2 }}</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, frauds=suspected_frauds, mae=mae, rmse=rmse, r2=r2)

@app.route('/')
def home():
    return 'Bienvenue sur l’API de détection de fraude. Accédez à /detect pour voir les résultats.'

if __name__ == '__main__':
    app.run(debug=True)
