from flask import Flask, request, jsonify
import openai
import os
from docx import Document

app = Flask(__name__)

# Set your API key via Render environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load knowledge base documents
kb_content = ""
kb_folder = "knowledge-base"

if os.path.exists(kb_folder):
    for root, dirs, files in os.walk(kb_folder):
        for file in files:
            if file.endswith(".docx"):
                try:
                    doc = Document(os.path.join(root, file))
                    for para in doc.paragraphs:
                        kb_content += para.text + "\n"
                except Exception as e:
                    kb_content += f"\n[Error reading {file}: {str(e)}]\n"

system_prompt = "You are a helpful assistant specialized in calendar management and executive support. Use the following knowledge base to answer questions when relevant:\n\n" + kb_content

@app.route("/")
def home():
    return "Custom GPT with Knowledge Base is running!"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
