import pytest

from helpers.ticket_bot.format_helpers import display_stock


@pytest.mark.unit
@pytest.mark.parametrize(
    ("stock", "expected"),
    [
        (-1, "∞"),
        (0, "OUT OF STOCK"),
        (3, 3),
    ],
)
def test_display_stock(stock, expected):
    assert display_stock(stock) == expected
