# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Tiến Huân
**Nhóm:** 11
**Ngày:** 05/07/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai chunk có vector embedding gần cùng hướng trong không gian vector được hiểu là high consine similarity, điều này thể hiện chúng có ngữ nghĩa tương đồng dù cách diễn đạt có thể khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: Tôi muốn đăng ký gói cước 5G của Viettel.
- Sentence B: Làm thế nào để kích hoạt dịch vụ 5G Viettel?
- Tại sao tương đồng: Cùng nói về dịch vụ 5G của Viettel.

**Ví dụ LOW similarity:**
- Sentence A: Tôi muốn đăng ký gói cước 5G của Viettel.
- Sentence B: Cách làm bánh mì tại nhà.
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ quan tâm đến hướng của vector nên phản ánh tốt hơn sự tương đồng ngữ nghĩa. Euclidean distance bị ảnh hưởng bởi độ lớn vector nên thường kém ổn định hơn với embeddings.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* (10000 - 50) / (500 - 50) = 22.11. Suy ra có 23 chunks.

> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> (10000 -100) / (500 - 100) = 25 chunks. Chunk count tăng vì bước nhảy nhỏ hơn. Overlap lớn giúp giữ ngữ cảnh giữa các chunk và giảm nguy cơ mất thông tin tại ranh giới chia đoạn.


---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Viettel Customer Support FAQ

**Tại sao nhóm chọn domain này?** 
> Bộ dữ liệu FAQ có cấu trúc rõ ràng theo dạng câu hỏi - trả lời nên rất phù hợp để đánh giá retrieval. Ngoài ra đây là dữ liệu tiếng Việt, giúp kiểm tra hiệu quả chunking và embedding trên ngôn ngữ tự nhiên.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Viettel - Mobile FAQs | Viettel | ~20k | source |
| 2 | Viettel - Internet - TV FAQs | Viettel | ~18k | source |
| 3 | Viettel - MyViettel FAQs | Viettel | ~15k | source |
| 4 | Viettel - Business Service FAQs | Viettel | ~17k | source |
| 5 | Viettel - Digital Application FAQs | Viettel | ~16k | category, source |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | viettel_faq | Truy vết nguồn dữ liệu |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| **Nguyễn Tiến Huân**<br>(Tôi - 2A202600855) | `SentenceChunker` | **8/10** | Cân bằng ngữ cảnh giữa các câu, ranh giới câu rõ ràng. | Tạo ra nhiều chunk hơn, dễ bị phân mảnh thông tin đối với các câu trả lời dài gồm nhiều ý. |
| **Phạm Thị Bích Ngọc**<br>(Tôi - 2A202600575) | `Custom QA Chunker`                                              |            **9.5/10**            | Giữ nguyên vẹn từng cặp Hỏi–Đáp, bảo toàn 100% ngữ cảnh của một cặp FAQ.                                                                                                                                                                                          | Kích thước chunk không đồng đều (lệ thuộc vào độ dài mục FAQ gốc). Khuyến nghị kết hợp logic đệ quy cho câu trả lời quá dài.                                                                                                 |
| **Phạm Huy Cảnh**<br>(2A202600663)            | `SentenceChunker` + `text-embedding-3-small` (Cloud API)         |            **9.5/10**            | Bảo toàn 100% ngữ cảnh câu và hiểu sâu từ đồng nghĩa tiếng Việt nhờ mô hình cloud chất lượng cao.                                                                                                                                                                 | Phụ thuộc hoàn toàn vào Cloud API (yêu cầu kết nối mạng và phát sinh chi phí).                                                                                                                                               |
| **Nguyễn Xuân Tới**<br>(2A202600810)          | `Recursive (Markdown-aware) + Greedy Merge` + `all-MiniLM-L6-v2` |            **9.5/10**            | - Separator Markdown-aware bảo toàn ranh giới Q&A.<br>- Q2 đạt top-1 score rất cao (0.7785).<br>- Greedy Merge giữ chunk ~800 ký tự giúp 4/5 query đạt STRONG hit (recall >= 50% trong top-3).<br>- Metadata domain lọc chính xác (4/5 top-1 đúng domain mobile). | - Q3, Q4 có top-1 score < 0.7 (semantic distance chưa tách rõ kết quả khỏi nhiễu).<br>- Rò rỉ chéo domain (Cross-domain leak): Q3(digital) lọt sang domain khác mobile, cần dùng `search_with_filter` để kiểm soát chặt hơn. |
| **Nguyễn Nam Thắng**<br>(2A202600840)         | `document-structure-chunking`                                    |             **9/10**             | - Giữ cấu trúc FAQ, nguồn rõ ràng.<br>- 5/5 query có chunk đúng nằm trong top-3.                                                                                                                                                                                  | - Tạo nhiều chunk hơn recursive baseline.<br>- Có query cần xem tới top-3 mới thấy đủ cú pháp SMS.                                                                                                                           |
| **Trần Trúc Quỳnh**<br>(2A202600934)          | `Q/A pair chunking` | **8/10** | Giữ trọn vẹn câu hỏi và câu trả lời đi kèm, dễ dàng cho việc grounding. | Chunk có thể rất dài nếu phần câu trả lời của FAQ quá dài. |


**Strategy nào tốt nhất cho domain này? Tại sao?**
> **Chiến lược tối ưu nhất cho domain FAQ này là các chiến lược chunking dựa trên cấu trúc tài liệu / cặp Hỏi - Đáp (đại diện là `Custom QA Chunker` của Phạm Thị Bích Ngọc, hoặc `Recursive (Markdown-aware) + Greedy Merge` của Nguyễn Xuân Tới).**
>
> **Lý do:**
>
> 1. **Bảo toàn tính toàn vẹn của thông tin**: Dữ liệu domain FAQ có ranh giới ngữ nghĩa tự nhiên và cực kỳ chặt chẽ giữa Câu hỏi (Question) và Câu trả lời (Answer). Các chiến lược baseline (như `FixedSizeChunker` hay `SentenceChunker`) chia cắt cơ học theo ký tự hoặc số câu dễ làm đứt đoạn, tách rời câu hỏi và câu trả lời sang các chunk khác nhau, khiến Vector Store không thể truy xuất đúng hoặc LLM bị thiếu ngữ cảnh trầm trọng.
> 2. **Hiệu năng truy xuất vượt trội**: Các phương pháp giữ nguyên cặp Q&A hoặc nhận biết cấu trúc Markdown đều đạt điểm retrieval xuất sắc (**9.0/10 - 9.5/10**). Khi truy vấn khớp với câu hỏi, toàn bộ câu trả lời đi kèm được trả về trọn vẹn giúp RAG Agent sinh câu trả lời chính xác, tránh hiện tượng sinh ảo (hallucination) hoặc trả lời cụt lủn.
> 3. **Tính độc lập và tối ưu chi phí**: Mặc dù giải pháp Sentence Chunker của Phạm Huy Cảnh đạt **9.5/10** nhờ dùng Cloud API (`text-embedding-3-small`), nhưng việc này tốn kém chi phí vận hành và phụ thuộc vào kết nối mạng. Ngược lại, chiến lược của Bích Ngọc và Xuân Tới vừa đạt hiệu năng cao tương đương (9.5/10), vừa tối ưu tài nguyên và có thể triển khai hoàn toàn offline/local.
> 4. **Khuyến nghị cải tiến kết hợp (Hybrid Strategy)**: Để giải quyết điểm yếu duy nhất của Custom QA Chunker (kích thước chunk không đồng đều), giải pháp tối ưu nhất thực tế là: **Sử dụng `QAChunker` làm khung phân tách chính**, sau đó áp dụng **`Recursive (Markdown-aware) Chunker` kết hợp `Greedy Merge`** để giới hạn độ dài tối đa (ví dụ ~800 ký tự) cho các câu trả lời quá dài. Điều này giúp vừa bảo toàn ranh giới Q&A, vừa kiểm soát số lượng token truyền vào LLM một cách ổn định nhất.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*

### Test Results

```
# Paste output of: pytest tests/ -v
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Metadata filtering giúp tăng độ chính xác retrieval đáng kể khi dữ liệu thuộc nhiều domain khác nhau.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ chuẩn hóa metadata chi tiết hơn và bổ sung các trường như service_type hoặc difficulty để hỗ trợ filtering hiệu quả hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
