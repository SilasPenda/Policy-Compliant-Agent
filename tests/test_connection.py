import os
import sys
from src.logger import logging

import pytest
from dotenv import load_dotenv

from src.utils import get_llm, db_client_connect


load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
llm_type = os.getenv("LLM_TYPE")
model_name = os.getenv("MODEL_NAME")
contract_collection = os.getenv("CONTRACT_COLLECTION_NAME")
policy_collection = os.getenv("POLICY_COLLECTION_NAME")


def test_llm_connection():
    """
    Test if the LLM can be instantiated and respond.
    """
    try:
        llm = get_llm(llm_type, model_name=model_name)
        response = llm.invoke("What is today's date?")

        assert response is not None, "LLM did not return a response."
        logging.info("LLM connection test passed.")

    except Exception as e:
        pytest.fail(f"Failed to connect to LLM '{llm_type}': {e}")

def test_db_connection():
    """
    Test the db_client_connect function.
    """
    contract_client = db_client_connect(contract_collection)
    policy_client = db_client_connect(policy_collection)

    assert contract_client is not None, "Failed to connect to the contract collection client."
    assert policy_client is not None, "Failed to connect to the policy collection client."
