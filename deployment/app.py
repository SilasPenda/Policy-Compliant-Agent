import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import gradio as gr

from src.utils import read_pdf, compute_confidence
from agent.templates import parser
from agent.reasoning import create_compliance_agent


# Gradio execution logic
def process_pdf_and_query(pdf_file, query):
    document_pages = read_pdf(pdf_file.name)
    texts = [page.extract_text() for page in document_pages if page.extract_text()]
    full_text = "\n\n".join(texts)

    agent_executor = create_compliance_agent(llm_type="openai", model_name="gpt-4o")

    response = agent_executor.invoke(
        {
            "query": query,
            "chunk": full_text,
        }
    )

    try:
        structured = parser.parse(response.get("output"))

        if structured.compliance_status == "Compliant":
            return f""" **Compliance Status:** {structured.compliance_status}

                **Compliant Policies:**
                {chr(10).join(f"- {p}" for p in structured.compliant_policies)}

                **Tools Used:**
                {chr(10).join(f"- {tool}" for tool in structured.tools_used)}

                **Similar Documents:**
                {chr(10).join(f"- {doc}" for doc in structured.similar_documents)}

                **Reasoning:**
                {structured.reasoning}
                """
        
        else:
            return f""" **Compliance Status:** {structured.compliance_status}

                **Violated Policies:**
                {chr(10).join(f"- {p}" for p in structured.violated_policies)}

                **Tools Used:**
                {chr(10).join(f"- {tool}" for tool in structured.tools_used)}

                **Similar Documents:**
                {chr(10).join(f"- {doc}" for doc in structured.similar_documents)}

                **Reasoning:**
                {structured.reasoning}
                """



        # return f""" **Compliance Status:** {structured.compliance_status}

        #         **Compliant Policies:**
        #         {chr(10).join(f"- {p}" for p in structured.compliant_policies)}

        #         **Violated Policies:**
        #         {chr(10).join(f"- {p}" for p in structured.violated_policies)}

        #         **Tools Used:**
        #         {chr(10).join(f"- {tool}" for tool in structured.tools_used)}

        #         **Similar Documents:**
        #         {chr(10).join(f"- {doc}" for doc in structured.similar_documents)}

        #         **Reasoning:**
        #         {structured.reasoning}
        #         """
    
        # return f""" **Compliance Status:** {structured.compliance_status}

        #         **Compliant Policies:**
        #         {structured.compliant_policies}

        #         **Violated Policies:**
        #         {structured.violated_policies}

        #         **Tools Used:**
        #         {structured.tools_used}

        #         **Similar Documents:**
        #         {structured.similar_documents}

        #         **Reasoning:**
        #         {structured.reasoning}
        #         """
    
    except Exception as e:
        print("Parser Error:", e)
        print("Raw LLM Output:", response)
        return f"Error occurred while parsing LLM response:\n{e}"


# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 📘 Document Compliance Assistant")

    with gr.Row():
        pdf_input = gr.File(label="Upload a PDF", file_types=[".pdf", ".PDF"])
        query = gr.Textbox(label="Compliance Question", placeholder="Enter your compliance question here...", lines=2)

    output = gr.Textbox(label="Compliance Report", lines=20, interactive=False)
    read_btn = gr.Button("Run Compliance Audit")

    read_btn.click(fn=process_pdf_and_query, inputs=[pdf_input, query], outputs=output)


app.launch(pwa=True, server_name="0.0.0.0", server_port=8501)
