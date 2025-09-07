-- 1) Extensions
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- tuỳ chọn

-- 2) Tạo text search configuration riêng (đặt trong schema rag để rõ ràng)
CREATE SCHEMA IF NOT EXISTS rag;

-- copy từ 'simple' rồi chèn bộ lọc unaccent
DROP TEXT SEARCH CONFIGURATION IF EXISTS rag.vi_unaccent;
CREATE TEXT SEARCH CONFIGURATION rag.vi_unaccent ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION rag.vi_unaccent
  ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple;


-- 3) Bảng document
CREATE TABLE IF NOT EXISTS rag.document (
  id         bigserial PRIMARY KEY,
  source_url text NOT NULL UNIQUE,
  title      text,
  language   text,
  checksum   bytea,
  created_at timestamptz DEFAULT now()
);


-- 4) Bảng chunk (đÃ sửa content_tsv để dùng regconfig thay vì hàm unaccent)
CREATE TABLE IF NOT EXISTS rag.chunk (
  id           bigserial PRIMARY KEY,
  document_id  bigint NOT NULL REFERENCES rag.document(id) ON DELETE CASCADE,
  ordinal      int    NOT NULL,
  content      text   NOT NULL,
  n_tokens     int,
  char_count   int,
  content_tsv  tsvector GENERATED ALWAYS AS (
    to_tsvector('rag.vi_unaccent'::regconfig, coalesce(content, ''))
  ) STORED,
  embedding    vector(1024) NOT NULL, -- 1024/384
  created_at   timestamptz DEFAULT now(),
  UNIQUE(document_id, ordinal)
);

-- 5) Indexes
CREATE INDEX IF NOT EXISTS idx_chunk_docid ON rag.chunk(document_id);
CREATE INDEX IF NOT EXISTS idx_chunk_tsv   ON rag.chunk USING GIN (content_tsv);
CREATE INDEX IF NOT EXISTS idx_chunk_vec_ivf_cos
  ON rag.chunk USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

