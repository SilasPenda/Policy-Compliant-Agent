import os
import sys
import uuid
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.exception import CustomException
from src.logger import logging
from src.utils import get_device, read_yaml, read_pdf


class Chunker:
    def __init__(self):
        root_dir = os.getcwd()
        self.contracts_dir = os.path.join(root_dir, "contracts")
        self.policies_dir = os.path.join(root_dir, "policies")

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def parse_contracts(self, pdf_path):
        try:
            texts = []
            metadatas = []
            ids = []

            reader_pages = read_pdf(pdf_path)
            for i, page in enumerate(reader_pages):
                text = page.extract_text()
                if text:
                    chunks = self.splitter.split_text(text)
                    for idx, chunk in enumerate(chunks):
                        texts.append(chunk)
                        metadatas.append({"page": i, "chunk": idx, "source": os.path.basename(pdf_path)})
                        # ids.append(f"{os.path.basename(pdf_path)}_page{i}_chunk{idx}")
            # ids = [i for i in range(len(texts))]
            ids = [str(uuid.uuid4()) for i in range(len(texts))]

            return texts, metadatas, ids
        
        except Exception as e:
            raise CustomException(e, sys)

    def parse_policies(self, yaml_path):
        try:
            texts = []
            metadatas = []
            ids = []

            data = read_yaml(yaml_path)

            for policy_category, rules in data.items():
                for rule in rules:
                    content = rule.get("content")
                    metadata = rule.get("metadata", {}).copy()

                    metadata.update({
                        "source_file": os.path.basename(yaml_path),
                        "policy_category": policy_category,
                    })

                    texts.append(content)
                    metadatas.append(metadata)
                    ids.append(str(uuid.uuid4()))

            return texts, metadatas, ids

        except Exception as e:
            raise CustomException(e, sys)
