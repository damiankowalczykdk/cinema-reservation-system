import unittest
from unittest.mock import patch, Mock

import pytest
from fastapi import HTTPException
from jwt import InvalidTokenError

from core import security


async def test_get_token_from_cookie() -> None:

    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    res = await security.get_token_from_cookie(token)

    assert res == "token1234"

async def test_get_current_user() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security._decode_token") as mock_decode:
        mock_decode.return_value = {"sub": "user123"}

        res = await security.get_current_user(token)

    assert res.sub == "user123"


async def test_get_current_user_invalid_token() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security._decode_token") as mock_decode:
        mock_decode.side_effect = InvalidTokenError()

        with pytest.raises(HTTPException) as e:
            await security.get_current_user(token)

        assert e.value.detail == "Could not validate credentials"


async def test_get_optional_current_user_not_token() -> None:
    token = unittest.mock.Mock(cookies={})

    with patch("core.security._decode_token") as mock_decode:
        mock_decode.return_value = {}

        res = await security.get_optional_current_user(token)


    assert res is None


async def test_get_optional_current_return_access_token() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security._decode_token") as mock_decode:
        mock_decode.return_value = {"sub": "user123"}

        res = await security.get_optional_current_user(token)


    assert res.sub == "user123"

async def test_get_optional_current_return_invalid_token() -> None:
    token = unittest.mock.Mock(cookies={"access_token": "token1234"})

    with patch("core.security._decode_token") as mock_decode:
        mock_decode.side_effect = InvalidTokenError()
        await security.get_optional_current_user(token)


def test_decode_token() -> None:

    with patch("core.security.jwks_client.get_signing_key_from_jwt") as mock_decode:
        mock_decode.return_value = Mock(key="dummy-public-key")

        with patch("core.security.jwt.decode") as md:
            md.return_value = {"sub": "user123"}

            payload = security._decode_token("dummy-public-key")

        assert payload == {"sub": "user123"}

