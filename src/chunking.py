from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # 1. Kiểm tra đầu vào, nếu rỗng thì trả về mảng rỗng
        if not text or not text.strip():
            return []
        
        # 2. Phân tách câu bằng Regex Lookbehind
        # Giải thích Regex: r'(?<=[.!?])\s+'
        # - (?<=[.!?]): Nhìn ngược về phía trước xem có dấu chấm, chấm than, hoặc hỏi chấm không.
        # - \s+: Tìm 1 hoặc nhiều khoảng trắng (bao gồm cả dấu cách " " và dấu xuống dòng "\n") ngay sau dấu câu đó để cắt.
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # 3. Lọc rác (Xóa các chuỗi rỗng do lỗi gõ phím hoặc khoảng trắng dư)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        
        # 4. Gom nhóm các câu theo kích thước (Batching)
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            # Lấy ra một nhóm câu (tối đa bằng max_sentences_per_chunk)
            batch = sentences[i : i + self.max_sentences_per_chunk]
            
            # Nối các câu lại với nhau bằng 1 khoảng trắng chuẩn, và strip hai đầu
            chunk_text = " ".join(batch).strip()
            chunks.append(chunk_text)
            
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        """Hàm bọc ngoài, khởi đầu quá trình đệ quy"""
        if not text or not text.strip():
            return []
        # Gọi hàm đệ quy với toàn bộ văn bản và toàn bộ danh sách bộ chia
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # ------------------------------------------------------------------
        # BASE CASE: Điểm dừng của đệ quy
        # Nếu đoạn text đã ngắn hơn mức cho phép, không cần cắt nữa!
        # ------------------------------------------------------------------
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # ------------------------------------------------------------------
        # BƯỚC 1: Tìm con dao (separator) to nhất có thể dùng
        # ------------------------------------------------------------------
        active_separator = remaining_separators[-1] # Mặc định là dao nhỏ nhất ("")
        next_separators = []

        for i, sep in enumerate(remaining_separators):
            # Nếu tìm thấy separator này trong đoạn văn bản (hoặc là chuỗi rỗng)
            if sep == "" or sep in current_text:
                active_separator = sep
                # Lưu lại các con dao nhỏ hơn để dành cho lần đệ quy sau
                next_separators = remaining_separators[i + 1:]
                break

        # ------------------------------------------------------------------
        # BƯỚC 2: Cắt đoạn văn bản bằng con dao vừa chọn
        # ------------------------------------------------------------------
        if active_separator == "":
            splits = list(current_text) # Cắt thành từng ký tự rời rạc
        else:
            splits = current_text.split(active_separator)

        # ------------------------------------------------------------------
        # BƯỚC 3: Duyệt qua các mảnh vụn vừa cắt. 
        # Nếu mảnh nào vẫn còn QUÁ TO, gọi đệ quy để cắt nó bằng con dao nhỏ hơn!
        # ------------------------------------------------------------------
        processed_splits = []
        for s in splits:
            if len(s) <= self.chunk_size:
                processed_splits.append(s) # Đã đủ nhỏ, giữ lại
            else:
                if next_separators:
                    # ĐỆ QUY: Mảnh này vẫn to, mang dao nhỏ hơn ra cắt tiếp
                    processed_splits.extend(self._split(s, next_separators))
                else:
                    # Hết dao: Bắt buộc phải cắt cơ học theo độ dài
                    for j in range(0, len(s), self.chunk_size):
                        processed_splits.append(s[j : j + self.chunk_size])

        # ------------------------------------------------------------------
        # BƯỚC 4: Gom (Merge) các mảnh vụn nhỏ lại thành Chunk lớn nhất có thể
        # ------------------------------------------------------------------
        final_chunks = []
        current_batch = []
        current_length = 0

        for s in processed_splits:
            # Tính độ dài nếu nhét thêm đoạn 's' vào khối hiện tại
            # (Phải cộng bù lại độ dài của ký tự chia cắt bị mất khi xài hàm split)
            sep_len = len(active_separator) if current_batch else 0
            new_len = current_length + sep_len + len(s)

            if new_len > self.chunk_size and current_batch:
                # Quá tải -> Gói khối hiện tại lại, cất đi. Mở khối mới chứa 's'
                final_chunks.append(active_separator.join(current_batch))
                current_batch = [s]
                current_length = len(s)
            else:
                # Vẫn còn chỗ trống -> Nhét 's' vào khối hiện tại
                current_batch.append(s)
                current_length = new_len

        # Đóng gói khối cuối cùng còn sót lại
        if current_batch:
            final_chunks.append(active_separator.join(current_batch))

        return final_chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # Đảm bảo hai vector có cùng số chiều (dimensions)
    if len(vec_a) != len(vec_b):
        raise ValueError("Hai vector phải có cùng kích thước (số chiều).")

    # 1. Tính tích vô hướng (Dot product): dot(a, b)
    dot_product = _dot(vec_a, vec_b)
    
    # 2. Tính độ lớn (Magnitude / Euclidean norm) của từng vector: ||a|| và ||b||
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    
    # 3. Xử lý ngoại lệ (Edge case): Tránh lỗi chia cho 0
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    # 4. Trả về kết quả cuối cùng
    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """
        Compare chunking strategies on the same text and return detailed metrics.
        
        Args:
            text: The text to chunk
            chunk_size: Target chunk size for FixedSizeChunker and RecursiveChunker
        
        Returns:
            Dictionary with comparison results for each strategy
        """
        if not text or not text.strip():
            return {
                "fixed_size": {"count": 0, "avg_length": 0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0, "chunks": []},
            }

        results = {
            "fixed_size": self._analyze_chunker(
                FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10),
                text,
            ),
            "by_sentences": self._analyze_chunker(
                SentenceChunker(max_sentences_per_chunk=5),
                text,
            ),
            "recursive": self._analyze_chunker(
                RecursiveChunker(chunk_size=chunk_size),
                text,
            ),
        }
        
        return results

    def _analyze_chunker(self, chunker, text: str) -> dict:
        """
        Analyze a single chunker strategy.
        
        Returns dict with:
            - chunks: list of generated chunks
            - count: total number of chunks
            - avg_length: average chunk size in characters
        """
        try:
            chunks = chunker.chunk(text)
            
            if not chunks:
                return {"chunks": [], "count": 0, "avg_length": 0}
            
            chunk_sizes = [len(chunk) for chunk in chunks]
            total_chars = sum(chunk_sizes)
            avg_size = total_chars / len(chunks) if chunks else 0
            
            return {
                "chunks": chunks,
                "count": len(chunks),
                "avg_length": round(avg_size, 2),
            }
        except Exception as e:
            return {"chunks": [], "count": 0, "avg_length": 0}
