# 🗺️ Embedding Model Configuration Map

## Sơ Đồ Cấu Trúc & Nơi Thay Đổi

```
┌─────────────────────────────────────────────────────────────────┐
│                    Embedding Model Configuration                  │
└─────────────────────────────────────────────────────────────────┘

                           ┌─────────────┐
                           │  main.py    │ 
                           │   (dòng 86) │
                           └──────┬──────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼────────┐    │    ┌────────▼───────┐
            │  Environment   │    │    │   Hardcoded    │
            │   Variables    │    │    │  in main.py    │
            │  (.env file)   │    │    │                │
            └───────┬────────┘    │    └────────┬───────┘
                    │             │             │
        ┌───────────▼──────────┐  │  ┌──────────▼──────────┐
        │EMBEDDING_PROVIDER=   │  │  │embedder =          │
        │  - mock              │  │  │LocalEmbedder()     │
        │  - local             │  │  │                    │
        │  - openai            │  │  └──────┬─────────────┘
        └───────────┬──────────┘  │         │
                    │             │         │
        ┌───────────▼──────────┐  │         │
        │ LOCAL/OPENAI MODEL   │  │         │
        │ LOCAL_EMBEDDING_MODEL│◄─┘         │
        │ OPENAI_EMBEDDING_    │            │
        │    MODEL             │            │
        └─────────────────────┘  ▼         ◄──┘
                                 │
                    ┌────────────▼──────────┐
                    │  src/embeddings.py    │
                    │  (dòng 6-8 constants) │
                    └────────────┬──────────┘
                                 │
                 ┌───────────────┴──────────────┐
                 │                              │
            ┌────▼─────────┐          ┌─────────▼───┐
            │LocalEmbedder │          │OpenAIEmbedder
            │ (Dùng model) │          │ (Dùng model)
            └────┬─────────┘          └─────────┬───┘
                 │                              │
                 │ all-MiniLM-L6-v2            │ text-embedding-3-small
                 │ all-mpnet-base-v2           │ text-embedding-3-large
                 │ distiluse-...               │
                 │                             │
                 └────────────┬────────────────┘
                              │
                 ┌────────────▼──────────┐
                 │   EmbeddingStore      │
                 │ (Vector Database)     │
                 └───────────────────────┘
```

---

## 📍 4 Điểm Thay Đổi Embedding Model

### Điểm 1: `.env` File (Cách 1 - Dễ Nhất)
```
📁 Root folder
├── .env  ◄─── THÊM/CHỈNH SỬA ĐÂY
│   EMBEDDING_PROVIDER=local
│   LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
│
├── main.py
├── src/
│   ├── embeddings.py
│   └── agent.py
└── data/
```

**Ưu điểm:**
- ✅ Không cần touch code
- ✅ Bật/tắt provider dễ dàng
- ✅ .env thường không commit

---

### Điểm 2: `src/embeddings.py` (Cách 2 - Hằng số mặc định)
```python
# src/embeddings.py - Dòng 6-8

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"  ◄─── THAY ĐỔI ĐÂY
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  ◄─── HOẶC ĐÂY

class LocalEmbedder:
    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL):
        # Sử dụng giá trị mặc định ở trên
```

**Ưu điểm:**
- ✅ Tất cả code tự động dùng model mới
- ✅ Trực tiếp, đơn giản

---

### Điểm 3: `main.py` (Cách 3 - Per-run configuration)
```python
# main.py - Dòng 86-100

def run_manual_demo(...):
    # ...
    
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        embedder = LocalEmbedder(
            model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL)
            #                                              ◄─── HOẶC thay hằng số ở đây
            # Hoặc hardcode: model_name="all-mpnet-base-v2"
        )
```

**Ưu điểm:**
- ✅ Chỉ ảnh hưởng main.py
- ✅ Linh hoạt per-run

---

### Điểm 4: Code tùy chỉnh (Cách 4 - Linh hoạt nhất)
```python
# Your custom code

from src.embeddings import LocalEmbedder, OpenAIEmbedder, _mock_embed
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

# ────── TẠO EMBEDDER THEO NƯỚC NGOÀI ──────
embedder = LocalEmbedder(model_name="all-mpnet-base-v2")  ◄─── TẠO ĐÂY

# ────── SỬ DỤNG TRONG AGENT ──────
store = EmbeddingStore(embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=your_llm)
```

**Ưu điểm:**
- ✅ Cách linh hoạt nhất
- ✅ Cho phép A/B test
- ✅ Per-instance customization

---

## 🎯 Decision Tree: Chọn Cách Nào?

```
┌─ Bạn muốn thay đổi embedding model ─┐
│                                      │
├─ "Tôi muốn dễ dàng bật/tắt"         ├─> ✅ CỐ 1: .env file
│  giữa các provider"                  │
│                                      │
├─ "Tôi muốn mặc định toàn cộng"      ├─> ✅ CỐ 2: src/embeddings.py
│  là model khác"                      │
│                                      │
├─ "Tôi chỉ thay đổi main.py"         ├─> ✅ CỐ 3: main.py
│  không muốn sửa code khác"           │
│                                      │
└─ "Tôi muốn linh hoạt, A/B test"     └─> ✅ CỐ 4: Custom code
   giữa các model"
```

---

## 💻 Ví Dụ Thực Tế

### Scenario 1: FAQ Tiếng Việt, Cần Nhanh
```bash
# .env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=distiluse-base-multilingual-cased-v2
```

### Scenario 2: Production, Chất Lượng Cao
```bash
# .env
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

### Scenario 3: Testing, Nhanh nhất
```bash
# .env
EMBEDDING_PROVIDER=mock
```

### Scenario 4: A/B Test trong Python
```python
models_to_test = [
    ("all-MiniLM-L6-v2", "Nhanh"),
    ("all-mpnet-base-v2", "Cân bằng"),
    ("distiluse-base-multilingual-cased-v2", "Đa ngôn ngữ"),
]

for model_name, description in models_to_test:
    embedder = LocalEmbedder(model_name=model_name)
    store = EmbeddingStore(embedding_fn=embedder)
    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)
    
    result = agent.answer(question)
    print(f"{description}: {result['score']}")
```

---

## 📊 Bảng Tóm Tắt

| Cách | File | Dòng | Dễ | Linh Hoạt | Trường Hợp |
|-----|------|------|----|---------|-----------:|
| 1 | .env | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Bật/tắt provider |
| 2 | src/embeddings.py | 6-8 | ⭐⭐ | ⭐ | Mặc định toàn code |
| 3 | main.py | 86-100 | ⭐⭐⭐ | ⭐⭐ | Per-run chỉnh sửa |
| 4 | Custom code | N/A | ⭐ | ⭐⭐⭐⭐⭐ | A/B test, prototype |

---

## ✅ Kết Luận

**Nên chọn:**
- 👉 **Cách 1 (.env)** - Hầu hết trường hợp
- 👉 **Cách 4 (Custom)** - Nếu đang thử nghiệm/A/B test

Tài liệu đầy đủ: `EMBEDDING_MODEL_GUIDE.md`
