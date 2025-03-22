import json
from datetime import datetime
from typing import Any

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_with_dates(obj: Any) -> str:
    """Serialize an object to JSON with datetime handling.
    
    Args:
        obj: The object to serialize
        
    Returns:
        JSON string representation
    """
    return json.dumps(obj, cls=DateTimeEncoder, indent=2)
