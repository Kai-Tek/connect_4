import json
from typing import Any, Dict, Optional


Message = Dict[str, Any]


def encode_message(message_type: str, **data: Any) -> bytes:
    message = {"type": message_type, **data}
    return encode_raw_message(message)


def encode_raw_message(message: Message) -> bytes:
    return (json.dumps(message) + "\n").encode("utf-8")


def decode_message(line: bytes) -> Message:
    return json.loads(line.decode("utf-8"))


def make_state_message(game, text: Optional[str] = None) -> Message:
    message = {
        "type": "state",
        "board": game.board,
        "current_player": game.current_player,
        "status": game.status.value,
        "moves_count": game.moves_count,
    }

    if text is not None:
        message["text"] = text

    return message
