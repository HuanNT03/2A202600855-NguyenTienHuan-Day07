from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Chuẩn hóa cấu trúc một bản ghi dựa trên định nghĩa Document mới.
        """
        # 1. Đổi từ "page_content"/"text" sang "content" theo thiết kế mới của bạn
        text = getattr(doc, "content", "")
        
        # 2. Lấy metadata (nếu không có thì trả về dict rỗng nhờ default_factory)
        metadata = getattr(doc, "metadata", {})
        
        # 3. Sử dụng luôn doc.id có sẵn làm ID cho bản ghi trong Vector Store.
        # Nếu doc.id rỗng hoặc không có, ta mới fallback về tự sinh số thứ tự.
        record_id = getattr(doc, "id", None)
        if not record_id:
            record_id = f"chunk_{self._next_index}"
            self._next_index += 1
        
        # Tạo vector embedding bằng MockEmbedder của bạn
        embedding = self._embedding_fn(text)
        
        return {
            "id": record_id,
            "text": text,
            "embedding": embedding,
            "metadata": metadata
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """
        Thực hiện tìm kiếm tương đồng (Similarity Search) thủ công trong bộ nhớ RAM.
        Sử dụng Dot Product để đo khoảng cách giữa Vector câu hỏi và Vector dữ liệu.
        """
        if not records:
            return []

        query_embedding = self._embedding_fn(query)
        scored_records = []
        
        for rec in records:
            # Sử dụng hàm toán học _dot được import từ module .chunking để tính độ tương đồng
            score = _dot(query_embedding, rec["embedding"])
            
            # Đóng gói lại cấu trúc trả về tương đương với định dạng Chroma trả về để đồng bộ hóa
            result_node = {
                "id": rec["id"],
                "content": rec["text"],
                "metadata": rec["metadata"],
                "score": score
            }
            scored_records.append(result_node)
            
        # Sắp xếp theo điểm tương đồng giảm dần (Dot product càng cao càng giống nhau)
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if self._use_chroma and self._collection is not None:
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            for doc in docs:
                record = self._make_record(doc)
                ids.append(record["id"])
                documents.append(record["text"])
                embeddings.append(record["embedding"])
                metadatas.append(record["metadata"])
            
            self._collection.add(
                ids=ids, 
                documents=documents, 
                embeddings=embeddings, 
                metadatas=metadatas
            )
        else:
            # Nhánh chạy chính hiện tại của bạn: Thêm dữ liệu vào RAM list
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(query_embeddings=[query_embedding], n_results=top_k)
            
            formatted_results = []
            if results and 'ids' in results and results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i] if results.get('documents') else "",
                        "metadata": results['metadatas'][0][i] if results.get('metadatas') else {},
                    })
            return formatted_results
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding], 
                n_results=top_k,
                where=metadata_filter
            )
            
            formatted_results = []
            if results and 'ids' in results and results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i] if results.get('documents') else "",
                        "metadata": results['metadatas'][0][i] if results.get('metadatas') else {},
                    })
            return formatted_results
        else:
            # Áp dụng bộ lọc Metadata trước (Pre-filtering) đối với bộ nhớ RAM
            if not metadata_filter:
                filtered_records = self._store
            else:
                filtered_records = []
                for rec in self._store:
                    is_match = True
                    for key, val in metadata_filter.items():
                        if rec["metadata"].get(key) != val:
                            is_match = False
                            break
                    if is_match:
                        filtered_records.append(rec)
            
            # Sau khi lọc xong mới đem đi so sánh độ tương đồng vector
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            try:
                initial_count = self._collection.count()
                self._collection.delete(where={"doc_id": doc_id})
                return self._collection.count() < initial_count
            except Exception:
                return False
        else:
            initial_size = len(self._store)
            # Giữ lại các khối KHÔNG có ID trùng khớp với doc_id được chỉ định
            self._store = [rec for rec in self._store if rec["id"] != doc_id]
            return len(self._store) < initial_size
