import unittest
from unittest.mock import patch, Mock

import pytest
from fastapi import HTTPException
from jwt import InvalidTokenError

from core import security



async def test_get_current_user_success() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security.jwks_client.get_signing_key_from_jwt"), \
        patch("core.security.jwt.decode") as mock_decode:

        mock_decode.return_value = {"sub": "user123"}

        res = await security.get_current_user(token)


    assert res is not None
    assert res.sub == "user123"


async def test_get_current_user_invalid_token() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security.jwks_client.get_signing_key_from_jwt"), \
        patch("core.security.jwt.decode") as mock_decode:

        mock_decode.side_effect = InvalidTokenError()

        res = await security.get_current_user(token)

    assert res is None


