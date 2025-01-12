# MAS is all you need: supercharge your Retrieval-Augmented Generation (RAG) with Multi-Agent Systems

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