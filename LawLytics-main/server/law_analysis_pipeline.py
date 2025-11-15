# law_analysis_pipeline.py
from preprocess_utils import preprocess_with_comprehend
from summarize_law_texts_bedrock import summarize_with_bedrock
import json

if __name__ == "__main__":
    print("⚙️ Lancement du pipeline complet (Comprehend + Bedrock)...")

    # 1️⃣ Lecture du texte source
    try:
        with open("data/2.H.R.1 - One Big Beautiful Bill Act.xml", "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open("data/2.H.R.1 - One Big Beautiful Bill Act.xml", "r", encoding="latin-1", errors="ignore") as f:
            text = f.read()

    # 2️⃣ Extraction sémantique
    results, s3_path = preprocess_with_comprehend(text)

    print(f"✅ {len(results['entities'])} entités et {len(results['key_phrases'])} phrases clés détectées.")
    print(f"📤 Résultats uploadés sur : {s3_path}")


    # 3️⃣ Résumé analytique
    summary = summarize_with_bedrock(text)
    print("\n🧾 Résumé final :\n")
    print(summary)

    # 4️⃣ Sauvegarde du rapport combiné
    report = {
        "entities": results["entities"],
        "key_phrases": results["key_phrases"],
        "summary": summary
    }

    with open("data/final_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n📦 Rapport complet enregistré sous data/final_report.json")
