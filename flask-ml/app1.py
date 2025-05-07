from flask import Flask, render_template_string, request
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import io
import base64

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def forecast():
    image_base64 = ""
    annee = ""
    
    if request.method == "POST":
        annee = request.form.get("annee")
        if annee and annee.isdigit():
            annee = int(annee)

            # Charger le modèle Prophet
            model = joblib.load('modele_candidatures_prophet.pkl')

            # Générer les futures dates
            future = model.make_future_dataframe(periods=48, freq='M')
            forecast = model.predict(future)

            # Filtrer uniquement l'année demandée
            forecast['ds'] = pd.to_datetime(forecast['ds'])
            forecast_filtered = forecast[forecast['ds'].dt.year == annee]

            # S'assurer qu'on a des données à afficher
            if not forecast_filtered.empty:
                fig, ax = plt.subplots()
                ax.plot(forecast_filtered['ds'], forecast_filtered['yhat'], label="Prévision")
                ax.fill_between(forecast_filtered['ds'], forecast_filtered['yhat_lower'], forecast_filtered['yhat_upper'], alpha=0.3)
                ax.set_title(f"Prévisions pour l'année {annee}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Nombre de candidatures")
                ax.legend()

                buf = io.BytesIO()
                plt.tight_layout()
                fig.savefig(buf, format="png")
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                buf.close()
                plt.close(fig)
            else:
                image_base64 = None

    # HTML avec formulaire
    html = """
    <html>
    <head><title>Prévision Candidatures</title></head>
    <body>
        <h1>Prédiction du nombre de candidatures</h1>
        <form method="post">
            <label for="annee">Entrez une année :</label>
            <input type="text" name="annee" required>
            <input type="submit" value="Prédire">
        </form>
        {% if image %}
            <h2>Résultat pour l'année {{ annee }}</h2>
            <img src="data:image/png;base64,{{ image }}" alt="Prévision">
        {% elif image is not none %}
            <p>Aucune donnée de prévision pour l'année {{ annee }}.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, image=image_base64, annee=annee)

if __name__ == "__main__":
    app.run(debug=True)
