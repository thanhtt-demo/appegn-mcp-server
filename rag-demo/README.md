# RAG Demo with Local Embeddings and PostgreSQL pgvector

This demo showcases a Retrieval-Augmented Generation (RAG) system using local Vietnamese embeddings and PostgreSQL with the pgvector extension for vector similarity search.

## Overview

The system demonstrates:
- **Document Processing**: Fetching and cleaning Vietnamese Wikipedia content
- **Text Chunking**: Advanced paragraph-based text splitting optimized for Vietnamese
- **Local Embeddings**: Using HuggingFace Vietnamese embedding models
- **Vector Storage**: PostgreSQL with pgvector extension for efficient similarity search
- **Hybrid Search**: Combining semantic search with full-text search using Reciprocal Rank Fusion (RRF)

## Features

- 🇻🇳 **Vietnamese Language Support**: Optimized for Vietnamese text processing with pyvi tokenization
- 🔍 **Hybrid Search**: Combines semantic similarity and full-text search for better results
- 🏠 **Local Embeddings**: No external API calls required - runs completely offline
- 📊 **PostgreSQL Integration**: Efficient vector storage and retrieval with pgvector
- 📝 **Smart Text Chunking**: Paragraph-based chunking with word count optimization

## Prerequisites

### Database Setup

1. **Quick Setup**: Run the provided SQL script to install extensions and create tables:
   ```bash
   psql -d your_database -f install-extensions-create-tables.sql
   ```

2. **Manual Setup** (if you prefer step-by-step):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   
   CREATE SCHEMA IF NOT EXISTS rag;
   
   CREATE TABLE rag.document (
       id SERIAL PRIMARY KEY,
       source_url TEXT UNIQUE NOT NULL,
       title TEXT,
       language TEXT,
       checksum BYTEA,
       created_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE TABLE rag.chunk (
       id SERIAL PRIMARY KEY,
       document_id INTEGER REFERENCES rag.document(id),
       ordinal INTEGER,
       content TEXT,
       content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
       n_tokens INTEGER,
       char_count INTEGER,
       embedding VECTOR(768), -- Adjust dimension based on your model
       created_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE INDEX ON rag.chunk USING GIN(content_tsv);
   CREATE INDEX ON rag.chunk USING ivfflat (embedding vector_cosine_ops);
   ```

### Environment Variables
Create a `.env` file with the following variables:
```env
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=your_database
PG_USER=your_username
PG_PASSWORD=your_password
AWS_REGION=us-east-1
HUGGINGFACEHUB_API_TOKEN=your_hf_token  # Optional, for some models
```

## Installation

1. **Setup Database**:
   ```bash
   # Run the SQL installation script
   psql -d your_database -f install-extensions-create-tables.sql
   ```

2. **Install Python dependencies**:
   ```bash
   pip install "langchain>=0.2.16" "langchain-aws>=0.2.2" boto3 requests beautifulsoup4 psycopg2-binary tqdm sentence-transformers langchain_community pyvi
   ```

3. **Clone and setup**:
   ```bash
   git clone <repository>
   cd rag-demo
   ```

4. **Configure environment**:
   - Copy `.env.example` to `.env`
   - Update database connection details
   - Add HuggingFace token if required

## Usage

### Running the Demo

Open and run the Jupyter notebook `rag-local.ipynb`:

```bash
jupyter notebook rag-local.ipynb
```

The notebook will:
1. **Fetch Vietnamese Wikipedia content** about the Vietnam War
2. **Process and chunk the text** using optimized paragraph-based splitting
3. **Generate embeddings** using local Vietnamese models
4. **Store vectors** in PostgreSQL with pgvector
5. **Demonstrate search capabilities** with both semantic and hybrid search

### Key Components

#### 1. Text Processing
- **Document Fetching**: Downloads and cleans Wikipedia content
- **Smart Chunking**: Splits text by paragraphs with 10-200 word limits
- **Vietnamese Optimization**: Uses pyvi for proper tokenization

#### 2. Embedding Models
Supported Vietnamese embedding models:
- `AITeamVN/Vietnamese_Embedding` (default)
- `dangvantuan/vietnamese-embedding`
- `sentence-transformers/all-MiniLM-L6-v2`

#### 3. Search Methods

**Semantic Search**:
```python
# Vector similarity search
rows = semantic_search(conn, query_vector, top_k=5)
```

**Hybrid Search (RRF)**:
```python
# Combines semantic + full-text search
rows = hybrid_search(conn, query_text, query_vector, top_k=5)
```

## Example Queries

The demo includes example Vietnamese queries:
- "Mối liên hệ giữa chiến tranh Việt Nam và chiến tranh Đông Phương ?"
- (Relationship between Vietnam War and Eastern conflicts?)

## Configuration

### Chunk Size Optimization
- **Minimum**: 10 words per chunk
- **Maximum**: 200 words per chunk
- **Method**: Paragraph-based with sentence splitting for large paragraphs

### Vector Dimensions
The system auto-detects embedding dimensions:
- AITeamVN/Vietnamese_Embedding: 768 dimensions
- Adjust database schema accordingly

## Performance Notes

- **Local Processing**: All embeddings generated locally (CPU/GPU)
- **Batch Processing**: Efficient bulk vector insertion
- **Index Optimization**: Uses ivfflat index for fast similarity search
- **Hybrid RRF**: Combines multiple ranking signals with k=60

## Troubleshooting

### Common Issues

1. **pgvector extension not found**:
   ```bash
   # Install pgvector extension
   sudo apt-get install postgresql-15-pgvector
   ```

2. **Memory issues with large models**:
   - Use smaller embedding models
   - Adjust batch sizes in processing

3. **Vietnamese tokenization errors**:
   - Ensure pyvi is properly installed
   - Fallback to simple word splitting available

### Database Connection Issues
- Verify PostgreSQL is running
- Check connection parameters in `.env`
- Ensure database and schema exist

## Extensions

This demo can be extended with:
- **Multiple document sources**: Add more Wikipedia pages or documents
- **Real-time updates**: Implement document change detection
- **API endpoints**: Wrap in FastAPI for web service
- **Advanced chunking**: Implement semantic chunking strategies
- **Multilingual support**: Add support for other languages

## License

This project is for demonstration purposes. Please respect Wikipedia's terms of use when scraping content.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## References

- [pgvector](https://github.com/pgvector/pgvector): PostgreSQL vector similarity search
- [LangChain](https://langchain.com/): Framework for LLM applications
- [HuggingFace Transformers](https://huggingface.co/transformers/): Pre-trained models
- [pyvi](https://github.com/trungtv/pyvi): Vietnamese language processing
