"""
缓存模块
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib
import json


class Cache:
    """
    简单的内存缓存
    """
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[Any, datetime]] = {}
    
    def _hash_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        """
        hashed = self._hash_key(key)
        if hashed in self._cache:
            value, expires_at = self._cache[hashed]
            if datetime.now() < expires_at:
                return value
            del self._cache[hashed]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        设置缓存
        """
        hashed = self._hash_key(key)
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        self._cache[hashed] = (value, expires_at)
    
    def delete(self, key: str):
        """
        删除缓存
        """
        hashed = self._hash_key(key)
        self._cache.pop(hashed, None)
    
    def clear(self):
        """
        清空缓存
        """
        self._cache.clear()
    
    def cleanup(self):
        """
        清理过期缓存
        """
        now = datetime.now()
        expired = [k for k, (_, exp) in self._cache.items() if now >= exp]
        for k in expired:
            del self._cache[k]
