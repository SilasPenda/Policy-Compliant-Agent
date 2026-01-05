import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import tempfile
from flask import Flask, request, jsonify

from src.utils import read_pdf, compute_confidence
from agent.templates import parser
from agent.reasoning import create_compliance_agent


app = Flask(__name__)

def run_agent(agent_executor, query, pdf_path):
    document_pages = read_pdf(pdf_path)
    texts = [
        page.extract_text()
        for page in document_pages
        if page.extract_text()
    ]

    if not texts:
        return jsonify({"error": "No text extracted from PDF"}), 400

    full_text = "\n\n".join(texts)

    response = agent_executor.invoke(
        {
            "query": query,
            "chunk": full_text,
        }
    )

    structured_response = parser.parse(response.get("output"))

    return structured_response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/compliance/check", methods=["POST"])
def process():
    """
    Accepts:
    - multipart/form-data:
        - file: PDF
        - query: string
    """

    try:
        agent_executor = create_compliance_agent(llm_type="openai", model_name="gpt-4o")
        if "file" not in request.files:
            return jsonify({"error": "PDF file is required"}), 400

        pdf_file = request.files["file"]
        query = request.form.get("query")

        if not query:
            return jsonify({"error": "Query is required"}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_file.save(tmp.name)
            pdf_path = tmp.name

        structured_response = run_agent(agent_executor, query, pdf_path)
        confidence_score = compute_confidence(structured_response)

        return jsonify(
            {
                "verdict": structured_response.compliance_status,
                "compliant_policies": structured_response.compliant_policies,
                "violated_policies": structured_response.violated_policies,
                "tools_used": structured_response.tools_used,
                "similar_documents": structured_response.similar_documents,
                "reasoning": structured_response.reasoning,
                "confidence": confidence_score,
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "verdict": "unknown",
                "policies": [],
                "tools_used": [],
                "similar_documents": [],
                "reasoning": "",
                "confidence": 0.0,
                "error": str(e),
            }
        ), 500

    finally:
        if "pdf_path" in locals() and os.path.exists(pdf_path):
            os.remove(pdf_path)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
