from django.core.cache import cache


class LocalEventBus:
    """
    Local implementation for monolith mode using cache
    """

    @staticmethod
    def publish(event_type, data, ttl=3600):
        """
        Publishes an event to the local bus
        Args:
            event_type (str): Event type (e.g., 'user.created')
            data (dict): Event data
            ttl (int): Time to live in seconds (default: 1h)
        """
        cache_key = f'event:{event_type}:{str(data.get("id", ""))}'
        cache.set(cache_key, data, timeout=ttl)

    @staticmethod
    def subscribe(event_type, callback, timeout=None):
        """
        Subscribe a function to events (mock)
        Args:
            event_type (str): Type of event to listen for
            callback (function): Function to execute
            timeout (int): Maximum wait time
        """
        # In local mode, it runs immediately
        # In production I would use Celery or similar
        cache_key = f'event:{event_type}:*'
        keys = cache.keys(cache_key)
        for key in keys:
            data = cache.get(key)
            if data:
                callback(data)
                cache.delete(key)


# Singleton for global use
event_bus = LocalEventBus()
