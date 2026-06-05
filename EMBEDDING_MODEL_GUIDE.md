# 🎯 Hướng Dẫn Thay Đổi Embedding Model

## 📍 Các Nơi Có Thể Thay Đổi Embedding Model

Có **4 cách chính** để thay đổi mô hình embedding, từ đơn giản đến phức tạp:

---

## 1️⃣ **Cách 1: Via Environment Variables (Dễ Nhất)**

### 📝 Sửa `.env` file
```bash
# Tạo/chỉnh sửa file .env trong root folder

# Chọn provider: mock, local, openai
EMBEDDING_PROVIDER=local

# Nếu dùng local (Sentence Transformers):
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Nếu dùng OpenAI:
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### ✅ Ưu điểm:
- Không cần sửa code
- Dễ bật/tắt giữa các model
- An toàn với Git (`.env` thường trong `.gitignore`)

### 📍 Vị trí file: `.env` (tạo mới trong root)

---

## 2️⃣ **Cách 2: Thay Đổi Hằng Số Mặc Định**

### 📝 Sửa `src/embeddings.py`
```python
# Dòng 6-8 trong src/embeddings.py

# TRƯỚC:
LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

# SAU (Ví dụ: Thay đổi model local):
LOCAL_EMBEDDING_MODEL = "all-mpnet-base-v2"  # Model mạnh hơn
# hoặc
LOCAL_EMBEDDING_MODEL = "distiluse-base-multilingual-cased-v2"  # Đa ngôn ngữ
```

### ✅ Ưu điểm:
- Tất cả code tự động dùng model mới
- Đơn giản, trực tiếp

### ⚠️ Nhược điểm:
- Phải sửa code
- Ảnh hưởng tất cả code dùng default

### 📍 Vị trí file: `src/embeddings.py` (dòng 6-8)

---

## 3️⃣ **Cách 3: Thay Đổi Khi Khởi Tạo Agent**

### 📝 Sửa `main.py`
```python
# Vị trí: main.py, dòng 86-100

# TRƯỚC:
embedder = LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))

# SAU (Cách 1 - Hardcode):
embedder = LocalEmbedder(model_name="all-mpnet-base-v2")

# SAU (Cách 2 - Lấy từ env):
embedder = LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", "all-mpnet-base-v2"))
```

### ✅ Ưu điểm:
- Chỉ ảnh hưởng main.py
- Linh hoạt per-run

### 📍 Vị trí file: `main.py` (dòng 86-98)

---

## 4️⃣ **Cách 4: Thay Đổi Khi Gọi Agent**

### 📝 Code tùy chỉnh
```python
from src.embeddings import LocalEmbedder, OpenAIEmbedder, _mock_embed
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

# ========== OPTION A: Local Model ==========
embedder = LocalEmbedder(model_name="all-mpnet-base-v2")
store = EmbeddingStore(embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=your_llm)

# ========== OPTION B: OpenAI Model ==========
embedder = OpenAIEmbedder(model_name="text-embedding-3-large")  # Model mạnh hơn
store = EmbeddingStore(embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=your_llm)

# ========== OPTION C: Mock (Testing) ==========
from src.embeddings import MockEmbedder
embedder = MockEmbedder(dim=128)  # Điều chỉnh kích thước vector
store = EmbeddingStore(embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=your_llm)
```

### ✅ Ưu điểm:
- Cách linh hoạt nhất
- Cho phép A/B test
- Per-instance customization

### 📍 Vị trí: Trong code của bạn khi khởi tạo agent

---

## 📊 So Sánh Các Model Embedding Phổ Biến

### Local Models (Sentence Transformers)
| Model | Ngôn Ngữ | Kích Thước | Tốc Độ | Chất Lượng |
|-------|---------|----------|--------|-----------|
| `all-MiniLM-L6-v2` | EN | Nhỏ | ⚡⚡⚡ | ⭐⭐⭐ |
| `all-mpnet-base-v2` | EN | Trung | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| `paraphrase-multilingual-mpnet-base-v2` | Đa | Trung | ⚡⚡ | ⭐⭐⭐⭐ |
| `distiluse-base-multilingual-cased-v2` | Đa | Nhỏ | ⚡⚡⚡ | ⭐⭐⭐⭐ |

### OpenAI Models
| Model | Kích Thước Output | Chi Phí | Chất Lượng |
|-------|------------------|--------|-----------|
| `text-embedding-3-small` | 1536 | $ | ⭐⭐⭐⭐ |
| `text-embedding-3-large` | 3072 | $$ | ⭐⭐⭐⭐⭐ |
| `text-embedding-ada-002` | 1536 | $ | ⭐⭐⭐ |

---

## 🎓 Trường Hợp Sử Dụng & Đề Xuất

### 📱 FAQ Tiếng Việt (Viettel)
**Đề xuất:** `distiluse-base-multilingual-cased-v2`
```python
embedder = LocalEmbedder(model_name="distiluse-base-multilingual-cased-v2")
```
- ✅ Hỗ trợ Tiếng Việt tốt
- ✅ Model nhỏ, nhanh
- ✅ Không cần API key

### 🚀 Chất Lượng Cao (Production)
**Đề xuất:** `text-embedding-3-large` (OpenAI)
```python
embedder = OpenAIEmbedder(model_name="text-embedding-3-large")
```
- ✅ Chất lượng tốt nhất
- ✅ Hỗ trợ tất cả ngôn ngữ
- ⚠️ Cần API key + chi phí

### ⚡ Nhanh & Tiết Kiệm (Demo/Testing)
**Đề xuất:** `all-MiniLM-L6-v2`
```python
embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")
```
- ✅ Model nhỏ nhất
- ✅ Tốc độ nhanh nhất
- ⚠️ Chất lượng trung bình

---

## 📋 Checklist Thay Đổi Embedding Model

### Nếu chọn Cách 1 (Env Variables):
- [ ] Tạo file `.env` trong root
- [ ] Thêm `EMBEDDING_PROVIDER=local`
- [ ] Thêm `LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2`
- [ ] Chạy lại: `python3 main.py`

### Nếu chọn Cách 2 (Hằng số):
- [ ] Mở `src/embeddings.py`
- [ ] Sửa dòng 6-8
- [ ] Chạy lại: `python3 main.py`

### Nếu chọn Cách 3 (main.py):
- [ ] Mở `main.py`
- [ ] Sửa dòng 89 hoặc 94
- [ ] Chạy lại: `python3 main.py`

### Nếu chọn Cách 4 (Code tùy chỉnh):
- [ ] Tạo script riêng hoặc notebook
- [ ] Import `LocalEmbedder` từ `src.embeddings`
- [ ] Tạo instance: `embedder = LocalEmbedder(model_name="...")`
- [ ] Truyền vào `EmbeddingStore`

---

## 🔗 Available Sentence Transformers Models

Danh sách đầy đủ: https://www.sbert.net/docs/pretrained_models.html

Một số model phổ biến:
- `all-mpnet-base-v2` - Tốt nhất để encoding chung
- `all-MiniLM-L6-v2` - Nhanh, nhỏ, tốt cho real-time
- `multi-qa-mpnet-base-dot-v1` - Tối ưu cho Q&A
- `paraphrase-multilingual-mpnet-base-v2` - Đa ngôn ngữ
- `distiluse-base-multilingual-cased-v2` - Multilingual, nhỏ

---

## ⚡ Quick Reference

```python
# ========== QUICK SETUP ==========

# ✅ Local (Default)
from src.embeddings import LocalEmbedder
embedder = LocalEmbedder()  # Dùng default all-MiniLM-L6-v2

# ✅ Local + Custom Model
from src.embeddings import LocalEmbedder
embedder = LocalEmbedder(model_name="all-mpnet-base-v2")

# ✅ OpenAI (Cần API key)
from src.embeddings import OpenAIEmbedder
embedder = OpenAIEmbedder()  # Dùng default text-embedding-3-small

# ✅ Mock (Testing only)
from src.embeddings import MockEmbedder
embedder = MockEmbedder(dim=384)  # Matches SBERT output size

# ========== THEN: Create Store & Agent ==========
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

store = EmbeddingStore(embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=your_llm_function)
```

---

**Tóm tắt:** Bạn có thể thay đổi embedding model ở **4 nơi khác nhau** tùy mục đích 🎯
