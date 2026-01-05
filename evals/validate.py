import os
import json

from src.utils import compute_confidence


def validate_output(test_id: str, output: dict):
    true_json_path = os.path.join(os.getcwd(), "evals", "true_output.json")
    
    with open(true_json_path) as f:
        true_output = json.load(f)

    true_verdict = true_output[test_id]["verdict"]

    pred_verdict = output.compliance_status
    confidence_score = compute_confidence(output)

    return {
        "test_id": test_id,
        "true_verdict": true_verdict,
        "pred_verdict": pred_verdict,
        "confidence_score": confidence_score
    }


