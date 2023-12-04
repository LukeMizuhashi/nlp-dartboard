from openai import OpenAI
from sample import Patent
import json
import tiktoken

class OpenAiClient:
    def __init__(self, open_ai_embedding_model: str, max_tokens: int):
        self.client = OpenAI()
        self.embedding_model = open_ai_embedding_model
        self.max_tokens = max_tokens

    def get_embedding(self, patent: Patent):
        """
        Function to get the embedding of a given Patent using OpenAI's embedding model.

        Example usage:
        embedding = client.get_embedding(patent)
        print(embedding.data[0].embedding)

        Args:
            text (str): The text string for which the embedding is to be generated.
        """
        patent_str = json.dumps(patent.row)
        enc = tiktoken.encoding_for_model(self.embedding_model)
        tokens = enc.encode(patent_str)
        print(len(tokens), self.max_tokens, len(tokens) > self.max_tokens)
        # response = self.client.embeddings.create(
        #     input=text,
        #     model=self.embedding_model
        # )
        # return response
