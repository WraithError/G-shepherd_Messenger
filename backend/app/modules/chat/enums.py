from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    SYSTEM = "system"


class ConversationType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    CHANNEL = "channel"


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WSEventType(str, Enum):
    # Incoming (client → server)
    SEND_MESSAGE = "send_message"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    MARK_READ = "mark_read"

    # Outgoing (server → client)
    NEW_MESSAGE = "new_message"
    USER_TYPING = "user_typing"
    USER_STOP_TYPING = "user_stop_typing"
    MESSAGE_READ = "message_read"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    ERROR = "error"
