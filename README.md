# MAS is all you need: supercharge your Retrieval-Augmented Generation (RAG) with Multi-Agent Systems

How to build a Multi-Agent RAG with AG2 and ChromaDB. 

Check the [Medium article](https://towardsdatascience.com/mas-is-all-you-need-f61f6e6f3aad) for the technical details.


## Local env creation

Create a `.env` file at the root, with the following:

```
OPENAI_API_KEY="<key>"
CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8001
```


## Python env creation

```bash
conda create -n "mas" python=3.12.8
conda activate mas
pip install -r requirements.txt
```

## Database initialization

```bash
chmod +x start_chroma
./start_chroma
```

## Ingestion of documents

```bash
chmod +x ingest
./ingest
```

## Start to chat

```bash
python mas.py
```
