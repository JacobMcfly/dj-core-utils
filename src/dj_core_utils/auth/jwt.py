from datetime import timedelta
from typing import Any, Dict, Optional


def get_jwt_config(
    signing_key: str,
    custom_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Gets JWT extensible configuration."""
    config: Dict[str, Any] = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': signing_key,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
    }

    if custom_config:
        config.update(custom_config)

    return config
