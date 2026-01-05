import os
import sys
from tqdm import tqdm
from qdrant_client import QdrantClient
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from dotenv import load_dotenv

from ingestion.chunking import Chunker
from ingestion.embed_upsert import EmbedUpsert
from src.exception import CustomException
from src.utils import get_next_collection_name

load_dotenv()


class PolicyIngestor:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        base_name = os.getenv("POLICY_COLLECTION_BASENAME")
        
        # Qdrant setup
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
            )
        
        self.collection_name = get_next_collection_name(self.client, base_name)
        self.policies_dir = os.path.join(os.getcwd(), base_name)
        self.chunker = Chunker()
        self.embed_upsert = EmbedUpsert(self.client)

    def run_pipeline(self):
        try:
            texts_list = []
            metadatas_list = []
            ids_list = []

            for root, dirs, files in os.walk(self.policies_dir):
                for file in tqdm(files, total=len(files), desc="Processing policy files"):
                    if file.endswith((".yaml", ".yml")):
                        yaml_path = os.path.join(root, file)
                        texts, metadatas, ids = self.chunker.parse_policies(yaml_path)

                        texts_list.extend(texts)
                        metadatas_list.extend(metadatas)
                        ids_list.extend(ids)

            embedings = self.embed_upsert.get_embeddings(texts_list)
            self.embed_upsert.upsert(texts_list, metadatas_list, ids_list, embedings, self.collection_name)

        except Exception as e:
            raise CustomException(e, sys)
        


if __name__ == "__main__":
    ingestor = PolicyIngestor()
    ingestor.run_pipeline()    

  