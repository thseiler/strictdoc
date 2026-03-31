import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from strictdoc.helpers.exception import StrictDocException


@dataclass
class DiscussionComment:
    raw_text: str

    comment_mid: str = field(init=False)
    timestamp_str: str = field(init=False)
    parsed_datetime: datetime = field(init=False)
    user: str = field(init=False)
    body: str = field(init=False)

    COMMENT_PATTERN = re.compile(r"^(\S+)\s+([^:]+):\s*(.*)", re.DOTALL)

    def __post_init__(self) -> None:
        match = self.COMMENT_PATTERN.match(self.raw_text.strip())

        if not match:
            raise StrictDocException(
                f"Syntax error in DISCUSSION comment. "
                f"Expected format 'ISO-TIMESTAMP username: text'.\n"
                f"Got: '{self.raw_text}'"
            )

        timestamp_str, user_str, body_str = match.groups()

        try:
            # The .replace("Z", "+00:00") is a safety measure to ensure compatibility
            # with Python versions older than 3.11, which didn't natively support the 'Z' suffix.
            parsed_datetime = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError as e:
            raise StrictDocException(
                f"Invalid timestamp in DISCUSSION comment: '{timestamp_str}'. "
                f"Must be a valid ISO 8601 format (e.g., 2023-10-24 or 2023-10-24T10:00:00Z).\nDetails: {e}"
            ) from e

        self.timestamp_str = timestamp_str
        self.parsed_datetime = parsed_datetime
        self.user = user_str.strip()
        self.body = body_str.strip()

        self.comment_mid = hashlib.md5(self.raw_text.strip().encode("utf-8")).hexdigest()

    @classmethod
    def create_new(cls, user: str, body: str) -> "DiscussionComment":
        """
        Factory method to safely format and create a new comment from scratch.
        """
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        safe_body = body.strip().replace("\n", "\n  ")
        new_comment_raw = f"{current_time} {user}: {safe_body}"

        return cls(raw_text=new_comment_raw)

    def is_resolved(self) -> bool:
        return "[RESOLVED]" == self.body.strip()

@dataclass
class DiscussionThread:
    thread_id: str

    comments: List[DiscussionComment] = field(default_factory=list)

    def is_resolved(self) -> bool:
        if not self.comments:
            return False
        # A thread is resolved if its very last comment is [RESOLVED]
        return self.comments[-1].is_resolved()

class DiscussionParser:
    """
    Translates a raw multiline string as found in the DISCUSSION: field of the SdocNode
    to and from structured Python objects.
    """

    @staticmethod
    def parse(raw_discussion_string: str) -> Dict[str, DiscussionThread]:
        if not raw_discussion_string or not raw_discussion_string.strip():
            return {}

        threads: Dict[str, DiscussionThread] = {}
        current_thread_id: Optional[str] = None
        current_comment_lines: List[str] = []

        def flush_comment():
            if current_thread_id and current_comment_lines:
                raw_text = "\n".join(current_comment_lines)
                threads[current_thread_id].comments.append(DiscussionComment(raw_text))
                current_comment_lines.clear()

        for line in raw_discussion_string.splitlines():
            # Skip empty lines
            if not line.strip():
                continue

            # Detect Thread Anchor (e.g., 'c-12345:' or 'node:')
            # It starts at column 0 and ends with a colon
            if not line.startswith(" ") and not line.startswith("-") and line.endswith(":"):
                flush_comment()
                current_thread_id = line[:-1].strip()
                if current_thread_id not in threads:
                    threads[current_thread_id] = DiscussionThread(current_thread_id)
                continue

            # Detect new comment (Starts with '- ')
            if line.startswith("- "):
                flush_comment()
                # Strip the '- ' prefix to isolate the raw text
                current_comment_lines.append(line[2:])
                continue

            # Detect continuation line (Starts with at least 2 spaces)
            if line.startswith("  ") and current_comment_lines is not None:
                # Strip exactly 2 spaces of indentation
                current_comment_lines.append(line[2:])
                continue

            # If we hit garbage that doesn't match the format, throw a strict error
            raise StrictDocException(
                f"Syntax error in DISCUSSION block. Unrecognized line formatting:\n'{line}'"
            )

        # Flush the final comment when we reach the end of the string
        flush_comment()

        return threads

    @staticmethod
    def serialize(threads: Dict[str, DiscussionThread]) -> str:
        """
        Serializes the dictionary of DiscussionThreads back into the strict
        YAML/Markdown/reST string format required by StrictDoc.
        """
        if not threads:
            return ""

        output_lines = []

        for thread_id, thread in threads.items():
            if not thread.comments:
                continue

            # 1. Add the anchor key (e.g., "node:" or "c-12345:")
            output_lines.append(f"{thread_id}:")
            output_lines.append("")

            # 2. Add each comment as a list item
            for comment in thread.comments:
                # Split the comment to handle multi-line continuations securely
                lines = comment.raw_text.splitlines()
                if not lines:
                    continue

                # The first line gets the hyphen prefix
                output_lines.append(f"- {lines[0]}")

                # Subsequent lines get a 2-space indentation
                for continuation_line in lines[1:]:
                    output_lines.append(f"  {continuation_line}")

            output_lines.append("") # Empty line between threads

        # Join and strip trailing whitespace to keep the AST perfectly clean
        return "\n".join(output_lines).rstrip() + "\n"