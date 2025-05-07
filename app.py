from flask import Flask, render_template, request
from model_utils import load_models, predict_sectors, predict_score
from specializations import specializations_data
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import torch

app = Flask(__name__)
sector_model, score_model, sentence_model, label_encoder = load_models()

@app.route("/", methods=["GET", "POST"])
def index():
    selected_specialization = ""
    profile = ""
    predictions = None
    score = None

    if request.method == "POST":
        selected_specialization = request.form.get("specialization")
        selected_skills = request.form.getlist("skills")
        profile = request.form.get("profile", "")

        if selected_specialization in specializations_data:
            if selected_skills:
                profile += " Skills: " + ", ".join(selected_skills)

            predictions = predict_sectors(profile, sector_model, sentence_model, label_encoder)
            score = predict_score(profile, score_model, sentence_model)

            labels = [f"{i+1}. {name}" for i, (name, _) in enumerate(predictions)]
            values = [p[1] for p in predictions]

            plt.figure(figsize=(6, 3))
            plt.barh(labels[::-1], values[::-1], color="#4CAF50")
            plt.xlim(0, 100)
            plt.xlabel("Probabilité (%)")
            plt.title("Top 3 secteurs prédits")
            plt.tight_layout()

            if os.path.exists("static/prediction_chart.png"):
                os.remove("static/prediction_chart.png")
            plt.savefig("static/prediction_chart.png")

    return render_template(
        "index.html",
        specializations=specializations_data,
        selected_specialization=selected_specialization,
        profile=profile,
        predictions=predictions,
        score=score
    )

if __name__ == "__main__":
    app.run(debug=True)
