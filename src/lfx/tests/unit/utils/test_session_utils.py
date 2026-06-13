from uuid import UUID

from lfx.utils.session_utils import normalize_session_id


def test_normalize_session_id_adds_dashes():
    assert normalize_session_id("121b21721d294d69bd143cf3632dc16c") == "121b2172-1d29-4d69-bd14-3cf3632dc16c"


def test_normalize_session_id_preserves_dashed_uuid():
    dashed = "121b2172-1d29-4d69-bd14-3cf3632dc16c"
    assert normalize_session_id(dashed) == dashed
    assert normalize_session_id(UUID(dashed)) == dashed


def test_normalize_session_id_named_session_unchanged():
    assert normalize_session_id("Session 04 Jun 2026") == "Session 04 Jun 2026"
