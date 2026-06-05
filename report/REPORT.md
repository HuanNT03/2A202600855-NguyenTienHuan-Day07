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
| Viettel - Mobile FAQs | FixedSizeChunker (`fixed_size`) | 42 | 480 | Trung bình |
| Viettel - Mobile FAQs | SentenceChunker (`by_sentences`) | 35 | 530 | Tốt |
| Viettel - Mobile FAQs | RecursiveChunker (`recursive`) | 31 | 590 | Rất tốt |

### Strategy Của Tôi

**Loại:** SentenceChunker 

**Mô tả cách hoạt động:**
> Strategy sử dụng regex để phát hiện ranh giới câu dựa trên dấu chấm, chấm hỏi và chấm than. Các câu được gom thành từng nhóm theo tham số max_sentences_per_chunk. Sau đó các câu trong cùng nhóm được nối lại thành một chunk hoàn chỉnh. Cách tiếp cận này tránh việc cắt giữa câu.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> FAQ thường có các câu trả lời ngắn và độc lập. Chunk theo câu giúp giữ nguyên ý nghĩa của từng cặp hỏi - đáp và giảm nhiễu khi retrieval.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Viettel - Mobile FAQs | FixedSizeChunker (`fixed_size`) | 42 | 480 | 6/10 |
| Viettel - Mobile FAQs | SentenceChunker (`by_sentences`) | 35 | 530 | 8/10 |
| Viettel - Mobile FAQs | RecursiveChunker (`recursive`) | 31 | 590 | 9/10 |

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
> Sử dụng regex `(?<=[.!?])\s+` để phát hiện ranh giới câu. Loại bỏ khoảng trắng dư và gom nhiều câu thành một chunk theo kích thước cấu hình.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán thử tách theo nhiều separator theo thứ tự ưu tiên. Nếu đoạn vẫn vượt quá chunk_size thì tiếp tục đệ quy với separator cấp thấp hơn. Base case là khi độ dài đoạn nhỏ hơn chunk_size hoặc không còn separator để chia.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi document được chuyển thành embedding và lưu dưới dạng record trong bộ nhớ. Khi search, query được embed và tính độ tương đồng bằng cosine similarity để xếp hạng.

**`search_with_filter` + `delete_document`** — approach:
> Filter metadata trước rồi mới thực hiện ranking. Delete bằng cách loại bỏ tất cả record có cùng document id.

### KnowledgeBaseAgent

**`answer`** — approach:
> Agent thực hiện retrieval top-k chunk liên quan, ghép thành context và nhúng vào prompt. LLM được yêu cầu chỉ trả lời dựa trên context để giảm hallucination.

### Test Results

```
# ========================================== test session starts ==========================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- ~/Day07-Labs/2A202600855-NguyenTienHuan-Day07/.venv/bin/python3
cachedir: .pytest_cache
rootdir: ~/Day07-Labs/2A202600855-NguyenTienHuan-Day07
collected 42 items                                                                                      

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED             [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                      [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED               [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                     [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED     [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED           [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED            [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED          [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                            [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED            [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                       [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                   [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                             [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED    [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED        [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED  [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED        [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                            [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED              [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                      [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED           [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED             [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED              [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                       [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                      [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                 [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED             [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED        [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED            [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                  [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED            [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED       [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED      [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED     [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

========================================== 42 passed in 0.06s ===========================================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Đăng ký 5G | Kích hoạt 5G | High | 0.92 | Có |
| 2 | Nạp tiền | Thanh toán cước | High | 0.85 | Có |
| 3 | Mở MyViettel | Làm bánh pizza | Low | 0.12 | Có |
| 4 | Internet cáp quang | WiFi gia đình | High | 0.81 | Có |
| 5 | Sim Viettel | Thời tiết hôm nay | Low | 0.08 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Cặp “Nạp tiền” và “Thanh toán cước” có điểm rất cao dù từ ngữ khác nhau. Điều này cho thấy embedding học được ngữ nghĩa thay vì chỉ so khớp từ khóa.

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
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 9 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **84 / 100** |
