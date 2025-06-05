from prometheus_client import Counter

EVENTS_PUBLISHED = Counter(
    'django_events_published_total',
    'Eventos publicados en Redis',
    ['event_type']
)

# En tu código al publicar:
# EVENTS_PUBLISHED.labels(event_type="orden_creada").inc()
