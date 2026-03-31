import pytest

from strictdoc.backend.sdoc.models.discussion import (
    DiscussionComment,
    DiscussionParser,
    DiscussionThread,
)
from strictdoc.helpers.exception import StrictDocException


def test_01_parse_valid_comment_string():
    """Proves the regex correctly splits the date, user (including emails), and body."""
    raw_text = "2023-10-24T10:00:00Z jane.doe+test@example.com: This is a multiline\ncomment body."
    comment = DiscussionComment(raw_text)

    assert comment.timestamp_str == "2023-10-24T10:00:00Z"
    assert comment.user == "jane.doe+test@example.com"
    assert comment.body == "This is a multiline\ncomment body."
    assert comment.is_resolved() is False


def test_02_is_resolved():
    """Proves a thread is considered resolved only if the last comment has the tag."""
    t1 = DiscussionThread(
        "c-1",
        [
            DiscussionComment("2023-10-24T10:00:00Z user: Issue!"),
            DiscussionComment("2023-10-25T10:00:00Z user: [RESOLVED]")
        ]
    )
    assert t1.is_resolved() is True

    t2 = DiscussionThread(
        "c-2",
        [
            DiscussionComment("2023-10-24T10:00:00Z user: [RESOLVED]"),
            DiscussionComment("2023-10-25T10:00:00Z user: Wait, it's broken again.")
        ]
    )
    assert t2.is_resolved() is False

    t3 = DiscussionThread(
        "c-3",
        [
            DiscussionComment("2023-10-24T10:00:00Z user: We should set this to [RESOLVED] now"),
        ]
    )
    assert t3.is_resolved() is False

def test_03_invalid_comment_date():
    """Proves invalid calendar dates are caught and rejected."""
    # November only has 30 days
    raw_text = "2023-11-31T10:00:00Z user_A: This should fail."

    with pytest.raises(StrictDocException, match="Invalid timestamp in DISCUSSION comment"):
        DiscussionComment(raw_text)


def test_04_invalid_comment_format():
    """Proves missing components (like the colon) trigger a syntax error."""
    raw_text = "2023-10-24T10:00:00Z user_A Forgot the colon here"

    with pytest.raises(StrictDocException, match="Expected format 'ISO-TIMESTAMP username: text'"):
        DiscussionComment(raw_text)


def test_05_round_trip_serialization():
    """Proves the parser reads and writes the exact same multiline structure."""
    original_sdoc_discussion_string = (
        "node:\n\n"
        "- 2023-10-24T10:00:00Z user_A: First comment.\n\n"
        "c-12345:\n\n"
        "- 2023-10-24T10:01:00Z wile.e.coyote@acme.com: Second comment?\n"
        "  It spans multiple lines.\n"
        "- 2023-10-25 lead: Fixed.\n"
    )

    threads = DiscussionParser.parse(original_sdoc_discussion_string)

    # Assert dictionary structure
    assert len(threads) == 2
    assert "node" in threads
    assert "c-12345" in threads
    assert len(threads["c-12345"].comments) == 2
    assert threads["c-12345"].comments[0].user == "wile.e.coyote@acme.com"

    # Serialize back to String
    re_serialized_string = DiscussionParser.serialize(threads)

    # Assert exact match
    assert original_sdoc_discussion_string == re_serialized_string


def test_06_parse_empty_string():
    """Proves empty inputs return empty dictionaries without crashing."""
    assert DiscussionParser.parse("") == {}
    assert DiscussionParser.parse("   \n  ") == {}


def test_07_invalid_structure():
    """Proves the parser rejects garbage lines."""
    bad_discussion = "Just a random sentence without a thread anchor"

    with pytest.raises(StrictDocException, match="Unrecognized line formatting"):
        DiscussionParser.parse(bad_discussion)

def test_08_invalid_list_items():
    """Proves the parser rejects missing hyphens."""
    # Note: If it doesn't start with "- " or "  " and isn't a key, it throws.
    bad_discussion = (
        "c-12345:\n"
        "2023-10-24T10:00:00Z user_A: Forgot the hyphen for the list"
    )

    with pytest.raises(StrictDocException, match="Unrecognized line formatting"):
        DiscussionParser.parse(bad_discussion)
