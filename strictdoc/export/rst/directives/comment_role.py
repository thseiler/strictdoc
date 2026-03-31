import re
from typing import Any, Dict, List, Optional, Tuple

from docutils import nodes
from docutils.parsers.rst.states import Inliner


def comment_role(
    _name: str,
    _rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """
    Parses :comment:`Visible text <thread-123>` into an HTML span.
    """
    # text contains everything inside the backticks.
    # Split the visible text from the <thread_id> using a regex.
    match = re.match(r'^(.*?)\s*<(.*?)>$', text)

    if match:
        visible_text = match.group(1).strip()
        thread_id = match.group(2).strip()
    else:
        # Graceful fallback: if the user forgets the <...>, 
        # we just render the text normally and flag the ID.
        visible_text = text.strip()
        thread_id = "unknown-thread"

    # Construct the raw HTML span for the frontend
    html_string = (
        f'<span class="comment-highlight" '
        f'data-controller="inline-comment" '
        f'data-action="click->inline-comment#open" '
        f'data-thread-id="{thread_id}">{visible_text}</span>'
    )

    html_node = nodes.raw(_rawtext, html_string, format="html")

    return [html_node], []
