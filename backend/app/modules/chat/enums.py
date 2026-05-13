"""Chat-related enums."""

from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
