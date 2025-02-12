from typing import Union

from bech32 import bech32_decode, bech32_encode, convertbits
from fastapi.datastructures import URL


def decode(lnurl: str) -> str:
    hrp, data = bech32_decode(lnurl)
    assert hrp
    assert data
    bech32_data = convertbits(data, 5, 8, False)
    assert bech32_data
    return bytes(bech32_data).decode()


def encode(url: Union[str, URL]) -> str:
    bech32_data = convertbits(str(url).encode(), 8, 5, True)
    assert bech32_data
    lnurl = bech32_encode("lnurl", bech32_data)
    return lnurl.upper()
