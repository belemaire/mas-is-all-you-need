import os
from typing import List, Dict, Union
from chromadb import HttpClient as chromadb_http_client # type: ignore
from dotenv import load_dotenv # type: ignore
from json import dumps
from argparse import ArgumentParser
from cachier import cachier # type: ignore
from tools_ingestion import get_embedding


@cachier(cache_dir='.cachier')
def retrieve(
    query : str, 
    n_results : int = 10,
    chroma_db_host : str = "", 
    chroma_db_port : int = -1, 
    collection_name : str = "chunks"
) -> List[Dict[str, Union[str, float]]]:
    """
    Retrieve relevant chunks from a ChromaDB collection based on a query.

    This function performs a semantic search on a specified ChromaDB collection
    using the provided query. It returns a list of the most relevant chunks,
    along with their metadata and similarity scores.

    Args:
        query (str): The search query string.
        n_results (int, optional): The number of results to return. Defaults to 
            10.
        chroma_db_host (str, optional): The host address of the ChromaDB server. 
            If not provided, it uses the CHROMA_DB_HOST environment variable or 
            defaults to 'localhost'.
        chroma_db_port (int, optional): The port number of the ChromaDB server. 
            If not provided, it uses the CHROMA_DB_PORT environment variable or 
            defaults to 8001.
        collection_name (str, optional): The name of the ChromaDB collection to 
            search. Defaults to "chunks".

    Returns:
        List[Dict[str, Union[str, float]]]: A list of dictionaries, each 
            containing:
            - 'uuid': The unique identifier of the chunk
            - 'distance': The similarity score (lower is more similar)
            - 'source': The source of the chunk
            - 'chunk': The text content of the chunk
    """
    if len(chroma_db_host) == 0:
        chroma_db_host = os.getenv('CHROMA_DB_HOST', 'localhost')
    if chroma_db_port < 0:
        chroma_db_port = int(os.getenv('CHROMA_DB_PORT', 8001))
    client = chromadb_http_client(
        host=chroma_db_host, 
        port=chroma_db_port
    )
    collection = client.get_collection(name=collection_name)
    query_emb = get_embedding(list_text=[query])
    results = collection.query(
        query_embeddings = query_emb, 
        n_results = n_results, 
        include = ["documents", "metadatas", "distances"]
    )
    list_output = []
    for mtdt, chunk, uuid, distance in zip(
        results["metadatas"][0], 
        results["documents"][0], 
        results['ids'][0], 
        results["distances"][0], 
    ):
        list_output.append(
            {
                "uuid": uuid, 
                "distance": distance, 
                "source": mtdt['chunk_source'], 
                "last_update": mtdt['last_update'], 
                "chunk": chunk
            }
        )
    return list_output


def retrieve_str(
    query : str, 
    n_results : int = 10
) -> str:
    """
    Retrieve and format search results as a JSON string.

    This function performs a semantic search using the given query and returns
    the results as a formatted JSON string. It wraps the `retrieve` function
    and converts its output to a human-readable string format.

    Args:
        query (str): The search query string.
        n_results (int, optional): The number of results to return. Defaults to 10.

    Returns:
        str: A JSON-formatted string containing the search results. Each result includes:
            - 'uuid': The unique identifier of the chunk
            - 'distance': The similarity score (lower is more similar)
            - 'source': The source of the chunk
            - 'chunk': The text content of the chunk
    """
    list_retrieved = retrieve(query=query, n_results=n_results)
    return dumps(list_retrieved, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Retrieve similar text chunks from a ChromaDB collection.'
    )
    parser.add_argument(
        '--query', type=str, help='Your query.', required=True
    )
    parser.add_argument(
        '--n_results', type=str, help='Number of returned results.', default=10
    )
    args = parser.parse_args()
    load_dotenv()
    print(retrieve_str(query=args.query, n_results=args.n_results))