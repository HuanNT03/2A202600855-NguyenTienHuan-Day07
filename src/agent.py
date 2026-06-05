from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # Lưu trữ reference đến Vector Store và hàm gọi LLM
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Thực hiện quy trình RAG chuẩn để trả lời câu hỏi dựa trên tri thức được cấu trúc.
        """
        # Bước 1: Sử dụng cấu trúc lưu trữ đã hoàn thiện ở câu trước để lấy ra các Chunk liên quan
        # Kết quả trả về là list các dict chứa trường "text"
        retrieved_records = self.store.search(query=question, top_k=top_k)
        
        # Gom nội dung văn bản của các chunk lại làm Context
        context_chunks = [rec["content"] for rec in retrieved_records]
        context = "\n---\n".join(context_chunks) if context_chunks else "Không tìm thấy tài liệu phù hợp."

        # Bước 2: Thiết kế Hệ thống Prompt (System Prompt lồng Context)
        # Chúng ta cài đặt tư duy nghiêm ngặt để giải bài toán so sánh định lượng (như vụ sale 60% > 50%)
        prompt = f"""Bạn là một trợ lý chăm sóc khách hàng chuyên nghiệp và trung thực. 
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác CHỈ dựa trên phần ngữ cảnh (Context) cung cấp dưới đây.

[BẮT ĐẦU NGỮ CẢNH]
{context}
[KẾT THÚC NGỮ CẢNH]

Yêu Cầu Nghiêm Ngặt:
1. Trả lời ngắn gọn, đúng trọng tâm câu hỏi.
2. Nếu ngữ cảnh không chứa thông tin để trả lời, hãy lịch sự từ chối (Ví dụ: "Tôi không tìm thấy thông tin này trong tài liệu hệ thống"). Tuyệt đối không tự bịa thông tin (Hallucination).
"""

        # Bước 3: Đẩy prompt sang cho mô hình ngôn ngữ xử lý và trả về kết quả
        answer_text = self.llm_fn(prompt)
        return answer_text
