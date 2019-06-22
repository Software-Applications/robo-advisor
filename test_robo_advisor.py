# pytest script for automated test

import pytest
import os
from app.robo_advisor import to_usd, to_fnum, get_response



def test_to_usd():
    assert to_usd(5) == "$5.00"
    assert to_usd(0.26) == "$0.26"
    assert to_usd(4.2) == "$4.20"
    assert to_usd(1000) == "$1,000.00"

def test_fnum():
    assert to_fnum(1000) == "1,000"
    assert to_fnum(1000000) == "1,000,000"

def test_get_response():
    symbol = "NFLX"

    parsed_response = get_response(symbol)

    assert isinstance(parsed_response, dict)
    assert "Meta Data" in parsed_response.keys()
    assert "Weekly Time Series" in parsed_response.keys()
    assert parsed_response["Meta Data"]["2. Symbol"] == symbol




