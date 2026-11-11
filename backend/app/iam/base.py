"""Interface IAM dùng chung. Giữ ý tưởng của PermRAG (check_access) và bổ sung
list_accessible_collections (tính access signature) + nguồn sự kiện thay đổi quyền.

Muốn thêm GCP/AWS: viết class con của AccessControlBase và ChangeEventSource (xem gcp_stub.py, aws_stub.py).
Module cache KHÔNG phụ thuộc vào mô hình phân quyền cụ thể (plan mục 4.4.1).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class UserContext:
    user_id: str               # sub trong token
    username: str
    roles: tuple[str, ...] = ()
    display_name: str = ""


@dataclass
class AccessChangeEvent:
    occurred_at: datetime
    kind: str                  # role_mapping | user_attribute | policy | other
    summary: str
    user_ids: list[str] = field(default_factory=list)   # rỗng + affects_all=True -> tính lại cho mọi user
    affects_all: bool = False
    raw: dict = field(default_factory=dict)


class AccessControlBase(ABC):
    namespace: str = "base"    # tiền tố cho collection id, ví dụ "keycloak:public"

    @abstractmethod
    def list_accessible_collections(self, user: UserContext) -> set[str]:
        """Tập collection (chưa gắn namespace) user được đọc, theo đánh giá của IAM gốc tại thời điểm gọi."""

    @abstractmethod
    def check_collections(self, user: UserContext, collections: set[str]) -> dict[str, bool]:
        """Kiểm tra quyền đọc từng collection (dùng cho post-verify, re-verify khi hit và audit)."""

    def context_attributes(self) -> list[str]:
        """Thuộc tính ngữ cảnh request ảnh hưởng tới quyết định (rỗng = không có)."""
        return []


class ChangeEventSource(ABC):
    @abstractmethod
    def poll(self) -> list[AccessChangeEvent]:
        """Trả các sự kiện thay đổi quyền mới kể từ lần poll trước."""
