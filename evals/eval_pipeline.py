import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from evals.validate import validate_output
from my_projects.Policy_Compliant_Agent.deployment.api import run_agent
from agent.reasoning import create_compliance_agent


test_prompts = {
    "test_1": "Does this contract have a termination clause?",
    "test_2": "Is this contract compliant with GDPR laws?",
}


def run_evaluation():
    results = []
    agent_executor = create_compliance_agent(llm_type="openai", model_name="gpt-4o")
    test_contract = os.path.join(os.getcwd(), "tests", "test_contract.pdf")

    for test_id, query in test_prompts.items():
        structured_output = run_agent(
            agent_executor,
            query=query,
            pdf_path=test_contract
        )
        validation_result = validate_output(test_id, structured_output)
        validation_result.update({"test_query": query})
        results.append(validation_result)

    return results



if __name__ == "__main__":
    eval_results = run_evaluation()
    for result in eval_results:
        print(f"Test ID: {result['test_id']}")
        print(f"True Verdict: {result['true_verdict']}")
        print(f"Pred Verdict: {result['pred_verdict']}")
        print(f"Confidence Score: {result['confidence_score']}")
        print("-" * 40)