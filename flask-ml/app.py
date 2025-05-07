from flask import Flask, request, render_template_string, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import io

app = Flask(__name__)

# Page d'accueil avec formulaire
@app.route('/', methods=['GET', 'POST'])
def index():
    cluster = None
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            score_final = float(request.form['score_final'])
            days_to_interview = int(request.form['days_to_interview'])
            age = int(request.form['age'])
            sexe = request.form['sexe']  # 'M' ou 'F'
            nationality = request.form['nationalite']
            region = request.form['gouvernorat']

            # Encodage manuel (simplifié)
            sexe_encoded = 0 if sexe == 'M' else 1
            nationality_encoded = hash(nationality) % 1000
            region_encoded = hash(region) % 1000

            # DataFrame pour le modèle
            df = pd.DataFrame([{
                'score_final': score_final,
                'days_to_interview': days_to_interview,
                'age': age,
                'sexe_encoded': sexe_encoded,
                'nationality_encoded': nationality_encoded,
                'region_encoded': region_encoded,
                'resultat': 'inconnu'
            }])

            # Charger le scaler et le modèle
            scaler = joblib.load('modele/scaler.pkl')
            kmeans = joblib.load('modele/modele_clusters.pkl')

            features = df[['score_final', 'days_to_interview', 'age',
                           'sexe_encoded', 'nationality_encoded', 'region_encoded']]
            scaled = scaler.transform(features)
            df['cluster'] = kmeans.predict(scaled)
            cluster = int(df['cluster'].iloc[0])

            # Sauvegarder la figure dans un tampon
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df, x='score_final', y='days_to_interview',
                            hue='cluster', palette='Set2', s=200)
            plt.title(f"Cluster prédicté : {cluster}")
            plt.xlabel("Score Final")
            plt.ylabel("Délai jusqu’à l’entretien (jours)")
            plt.grid(True)
            plt.tight_layout()

            # Sauvegarde dans un buffer en mémoire
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            return send_file(buf, mimetype='image/png')

        except Exception as e:
            return f"<h3>Erreur : {str(e)}</h3>"

    # Formulaire HTML
    form_html = """
    <html>
    <head><title>Prédiction de Cluster</title></head>
    <body>
        <h1>Entrer les données du candidat</h1>
        <form method="POST">
            Score Final: <input type="number" step="0.01" name="score_final" required><br><br>
            Délai jusqu’à l’entretien (jours): <input type="number" name="days_to_interview" required><br><br>
            Âge: <input type="number" name="age" required><br><br>
            Sexe: 
            <select name="sexe">
                <option value="M">Masculin</option>
                <option value="F">Féminin</option>
            </select><br><br>
            Nationalité: <input type="text" name="nationalite" required><br><br>
            Gouvernorat: <input type="text" name="gouvernorat" required><br><br>
            <input type="submit" value="Prédire le cluster">
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(debug=True)
