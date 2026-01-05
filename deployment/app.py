import gradio as gr
import requests

# Flask API endpoint
API_URL = "http://localhost:8000/compliance/check"

def process_pdf_and_query(pdf_file, query):
    if pdf_file is None or query.strip() == "":
        return "Please upload a PDF and enter a compliance question."

    try:
        # Send PDF and query to the API
        with open(pdf_file.name, "rb") as f:
            files = {"file": (pdf_file.name, f, "application/pdf")}
            data = {"query": query}
            response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code != 200:
            return f"API Error [{response.status_code}]: {response.text}"

        result = response.json()

        if "error" in result:
            return f"API returned an error: {result['error']}"

        # Format the response for Gradio output
        verdict = result.get("verdict", "Unknown")
        reasoning = result.get("reasoning", "")
        confidence = result.get("confidence", 0.0)

        if verdict == "Compliant":
            policies = result.get("compliant_policies", [])
            policies_text = "\n".join(f"- {p}" for p in policies)
        else:
            policies = result.get("violated_policies", [])
            policies_text = "\n".join(f"- {p}" for p in policies)

        tools_text = "\n".join(f"- {t}" for t in result.get("tools_used", []))
        similar_docs_text = "\n".join(f"- {d}" for d in result.get("similar_documents", []))

        return f"""**Compliance Status:** {verdict}
        
                **Policies:** 
                {policies_text}

                **Tools Used:**
                {tools_text}

                **Similar Documents:**
                {similar_docs_text}

                **Reasoning:**
                {reasoning}

                **Confidence:** {confidence:.2f}
                """

    except Exception as e:
        return f"Error contacting API: {e}"


# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 📘 Document Compliance Assistant (via API)")

    with gr.Row():
        pdf_input = gr.File(label="Upload a PDF", file_types=[".pdf", ".PDF"])
        query_input = gr.Textbox(label="Compliance Question", placeholder="Enter your compliance question here...", lines=2)

    output = gr.Textbox(label="Compliance Report", lines=20, interactive=False)
    run_btn = gr.Button("Run Compliance Audit")

    run_btn.click(fn=process_pdf_and_query, inputs=[pdf_input, query_input], outputs=output)

app.launch(pwa=True, server_name="0.0.0.0", server_port=8501)
