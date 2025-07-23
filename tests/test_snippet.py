import os
import sys
import pytest

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spx.spxsnippet import spxSnippet


def test_encrypt_decrypt():
    original_content = 'hello world'
    original_email = 'user@example.com'
    original_reference = 'ref123'

    snip = spxSnippet(content=original_content)
    snip.email = original_email
    snip.reference = original_reference

    snip.encrypt()
    key = snip.clearKey

    # after encryption content should not equal original and be bytes
    assert snip.content != original_content
    assert isinstance(snip.content, (bytes, bytearray))

    assert snip.decrypt(key) is True

    assert snip.content == original_content
    assert snip.email == original_email
    assert snip.reference == original_reference
