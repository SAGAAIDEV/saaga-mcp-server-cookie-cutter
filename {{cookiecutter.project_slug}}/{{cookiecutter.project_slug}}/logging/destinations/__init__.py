"""
Logging destination implementations.

This module contains various logging destination backends that implement
the LogDestination interface for pluggable logging storage.
"""

from .base import LogDestination, LogEntry
from .sqlite import SQLiteDestination
from .factory import LogDestinationFactory, DestinationConfig, MultiDestination

__all__ = [
    "LogDestination", 
    "LogEntry", 
    "SQLiteDestination", 
    "LogDestinationFactory", 
    "DestinationConfig", 
    "MultiDestination"
]

# Future destinations can be registered here
# Example:
# try:
#     from .elasticsearch import ElasticsearchDestination
#     LogDestinationFactory.register_destination('elasticsearch', ElasticsearchDestination)
# except ImportError:
#     pass  # Optional destination not available