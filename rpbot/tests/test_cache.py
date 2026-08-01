import unittest
import time
from utils.cache import SimpleCache


class TestCache(unittest.TestCase):
    def test_set_get(self):
        c = SimpleCache(ttl_seconds=10)
        c.set("key1", "value1")
        self.assertEqual(c.get("key1"), "value1")

    def test_ttl_expiracao(self):
        c = SimpleCache(ttl_seconds=1)
        c.set("key1", "value1")
        time.sleep(1.5)
        self.assertIsNone(c.get("key1"))

    def test_invalidate(self):
        c = SimpleCache(ttl_seconds=10)
        c.set("key1", "value1")
        c.invalidate("key1")
        self.assertIsNone(c.get("key1"))

    def test_invalidate_pattern(self):
        c = SimpleCache(ttl_seconds=10)
        c.set("user:123:ativo", "data1")
        c.set("user:123:outro", "data2")
        c.set("user:456:ativo", "data3")
        c.invalidate_pattern("user:123")
        self.assertIsNone(c.get("user:123:ativo"))
        self.assertIsNone(c.get("user:123:outro"))
        self.assertEqual(c.get("user:456:ativo"), "data3")


if __name__ == "__main__":
    unittest.main()
