"""Khung adapter cho GCP / AWS (CHƯA cài đặt, chỉ để thể hiện điểm mở rộng - plan mục 4.4.1, 4.7).

GCP:  list_accessible_collections -> với mỗi bucket (collection) gọi
      storage.buckets.testIamPermissions(["storage.objects.get"]) bằng credential của user (STS/impersonation).
      Sự kiện: Cloud Audit Logs (SetIamPolicy) -> Pub/Sub.
AWS:  mỗi collection = 1 S3 bucket/prefix; kiểm tra bằng IAM policy simulator (SimulatePrincipalPolicy)
      hoặc head_object một object đại diện (như PermRAG). Sự kiện: CloudTrail -> EventBridge.
"""
from __future__ import annotations

from .base import AccessControlBase, ChangeEventSource, UserContext


class GCPAccessControl(AccessControlBase):
    namespace = "gcp"

    def list_accessible_collections(self, user: UserContext) -> set[str]:
        raise NotImplementedError("GCP adapter chưa cài đặt (hướng mở rộng)")

    def check_collections(self, user: UserContext, collections: set[str]) -> dict[str, bool]:
        raise NotImplementedError


class AWSAccessControl(AccessControlBase):
    namespace = "aws"

    def list_accessible_collections(self, user: UserContext) -> set[str]:
        raise NotImplementedError("AWS adapter chưa cài đặt (hướng mở rộng)")

    def check_collections(self, user: UserContext, collections: set[str]) -> dict[str, bool]:
        raise NotImplementedError


class NotImplementedEventSource(ChangeEventSource):
    def poll(self):
        return []
