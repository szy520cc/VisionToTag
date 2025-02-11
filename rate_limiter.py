import json
import time
from threading import Lock
from typing import Dict, Optional


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity  # 桶的容量
        self.fill_rate = fill_rate  # 令牌填充速率
        self.tokens = capacity  # 当前令牌数量
        self.last_update = time.time()
        self.lock = Lock()

    def _add_tokens(self):
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * self.fill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._add_tokens()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class APIRateLimiter:
    def __init__(self, api_keys_file: str):
        self.api_keys_file = api_keys_file
        self.api_keys = self._load_api_keys()
        self.buckets: Dict[str, TokenBucket] = {}
        self.current_key_index = 0
        self.lock = Lock()

    def _load_api_keys(self) -> list:
        with open(self.api_keys_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['api_keys']

    def _get_bucket(self, api_key: dict) -> TokenBucket:
        key = api_key['api_key']['key']
        if key not in self.buckets:
            rpm_limit = api_key['api_key']['quota']['rpm_limit']
            self.buckets[key] = TokenBucket(rpm_limit, rpm_limit / 60.0)
        return self.buckets[key]

    def get_available_api_key(self) -> Optional[dict]:
        with self.lock:
            start_index = self.current_key_index
            while True:
                api_key = self.api_keys[self.current_key_index]
                if api_key['api_key']['status'] == 'active':
                    bucket = self._get_bucket(api_key)
                    if bucket.consume():
                        return api_key

                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                if self.current_key_index == start_index:
                    break

            return None

    def update_api_key_status(self, key: str, status: str):
        with self.lock:
            for api_key in self.api_keys:
                if api_key['api_key']['key'] == key:
                    api_key['api_key']['status'] = status
                    break

    def increment_usage_count(self, key: str):
        with self.lock:
            for api_key in self.api_keys:
                if api_key['api_key']['key'] == key:
                    api_key['api_key']['quota']['used_count'] += 1
                    break


# 使用示例
def get_rate_limiter():
    return APIRateLimiter('api_keys.json')


# 在需要发送API请求的地方
def make_api_request():
    rate_limiter = get_rate_limiter()
    api_key = rate_limiter.get_available_api_key()

    if api_key is None:
        raise Exception("No available API keys or rate limit exceeded")

    try:
        # 使用api_key进行API调用
        key = api_key['api_key']['key']
        # ... 执行API请求 ...

        # 更新使用计数
        rate_limiter.increment_usage_count(key)

    except Exception as e:
        # 如果API调用失败，标记key为不可用
        rate_limiter.update_api_key_status(key, 'inactive')
        raise e
