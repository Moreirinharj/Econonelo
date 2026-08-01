"""Cache simples em memória com TTL (tempo de vida)."""
import time


class SimpleCache:
    def __init__(self, ttl_seconds=60):
        self._cache = {}
        self._ttl = ttl_seconds
    
    def get(self, key):
        """Retorna valor do cache ou None se expirou/não existe."""
        if key not in self._cache:
            return None
        value, expires_at = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return value
    
    def set(self, key, value):
        """Adiciona valor ao cache com TTL."""
        expires_at = time.time() + self._ttl
        self._cache[key] = (value, expires_at)
    
    def invalidate(self, key):
        """Remove uma chave específica do cache."""
        if key in self._cache:
            del self._cache[key]
    
    def invalidate_pattern(self, pattern):
        """Remove todas as chaves que contêm o pattern."""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for k in keys_to_remove:
            del self._cache[k]
    
    def clear(self):
        """Limpa todo o cache."""
        self._cache.clear()


# Instância global do cache (TTL de 30 segundos)
cache = SimpleCache(ttl_seconds=30)
