from __future__ import annotations

from collections.abc import Sequence
from enum import IntEnum
from typing import Any, NoReturn

#
CSI = "\033["
"""Control Sequence Introducer."""

RESET = "\033[0m"
"""Reset ANSI code."""


class TextColor(IntEnum):
    """TextColor.

    Enum Members
    ------------
    ERROR
    WARNING
    BLACK
    RED
    GREEN
    YELLOW
    BLUE
    MAGENTA
    CYAN
    WHITE
    BRIGHT_BLACK
    BRIGHT_RED
    BRIGHT_GREEN
    BRIGHT_YELLOW
    BRIGHT_BLUE
    BRIGHT_MAGENTA
    BRIGHT_CYAN
    BRIGHT_WHITE
    BLACK_BG
    RED_BG
    GREEN_BG
    YELLOW_BG
    BLUE_BG
    MAGENTA_BG
    CYAN_BG
    WHITE_BG
    BRIGHT_BLACK_BG
    BRIGHT_RED_BG
    BRIGHT_GREEN_BG
    BRIGHT_YELLOW_BG
    BRIGHT_BLUE_BG
    BRIGHT_MAGENTA_BG
    BRIGHT_CYAN_BG
    BRIGHT_WHITE_BG
    RESET
    """

    ERROR = 31
    WARNING = 93
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97
    BLACK_BG = 40
    RED_BG = 41
    GREEN_BG = 42
    YELLOW_BG = 43
    BLUE_BG = 44
    MAGENTA_BG = 45
    CYAN_BG = 46
    WHITE_BG = 47
    BRIGHT_BLACK_BG = 100
    BRIGHT_RED_BG = 101
    BRIGHT_GREEN_BG = 102
    BRIGHT_YELLOW_BG = 103
    BRIGHT_BLUE_BG = 104
    BRIGHT_MAGENTA_BG = 105
    BRIGHT_CYAN_BG = 106
    BRIGHT_WHITE_BG = 107
    RESET = 0


class TextStyle(IntEnum):
    """TextStyle.

    Enum Members
    ------------
    BOLD
    ITALIC
    UNDERLINE
    SLOW_BLINK
    FAST_BLINK
    COLOR_INVERT
    RESET
    """

    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4
    SLOW_BLINK = 5
    FAST_BLINK = 6
    COLOR_INVERT = 7
    RESET = 0


def _get_ANSI_escape_code(
    color: TextColor | Sequence[TextColor] | None = None,
    style: TextStyle | Sequence[TextStyle] | None = None,
) -> str:
    """Get the ansi escape code.

    Parameters
    ----------
    color: TextColor | Sequence[TextColor] | None = None,
        The color for the text. This should be a member of the TextColor enum
        or it should be a Sequence of TextColor members.

    style: TextStyle | Sequence[TextStyle] | None = None,
        The style for the text. This should be a member of the TextStyle enum
        or it should be a Sequence of TextStyle members.

    Returns
    -------
    ansi_code: str
        The ansi escape code to get the color/style wanted.
    """
    if color is None and style is None:
        return RESET
    ansi_code = ""
    if color is not None:
        if isinstance(color, Sequence):
            for col in color:
                ansi_code += f"{CSI}{str(col.value)}m"
        else:
            ansi_code += f"{CSI}{str(color.value)}m"
    if style is not None:
        if isinstance(style, Sequence):
            for sty in style:
                ansi_code += f"{CSI}{str(sty.value)}m"
        else:
            ansi_code += f"{CSI}{str(style.value)}m"
    return ansi_code


def styled_text(
    text: str,
    color: TextColor | Sequence[TextColor] | None = None,
    style: TextStyle | Sequence[TextStyle] | None = None,
) -> str:
    """Formats the text with color/style codes.

    Parameters
    ----------
    color: TextColor | Sequence[TextColor] | None = None,
        The color for the text. This should be a member of the TextColor enum
        or it should be a Sequence of TextColor members.

    style: TextStyle | Sequence[TextStyle] | None = None,
        The style for the text. This should be a member of the TextStyle enum
        or it should be a Sequence of TextStyle members.

    Returns
    -------
    styled_string: str
        The text with any necessary escape codes to style the text.

    Example
    -------
    >>> print("some text " + styled_text("example", color=TextColor.RED) + " normal again.")
    >>>
    >>> print("more text " + styled_text("example", style=TextStyle.ITALIC) + " normal again.")
    >>>
    >>> styled = styled_text("fancy", color=TextColor.RED_BG, style=TextStyle.BOLD)
    >>> print(f"normal {styled} normal")
    >>>
    >>> styled2 = styled_text("fancy", color=[TextColor.BLUE, TextColor.RED_BG])
    >>> print(f"normal {styled2} normal")
    """
    ansi_code = _get_ANSI_escape_code(color=color, style=style)
    styled_string = f"{ansi_code}{text}{RESET}"
    return styled_string


def styled_type_error(variable: Any, variable_name: str, correct_type: Any) -> NoReturn:
    """Formats the variable given into a colored type error.

    Parameters
    ----------
    variable: Any
        The variable to raise type error for.

    variable_name: str
        The name of the variable with the incorrect type.

    correct_type: Any
        The correct type that variable should be.
    """
    raise TypeError(
        f"`{variable_name}` should be of type "
        + styled_text(f"{correct_type}", color=TextColor.GREEN)
        + f".\nFound type `{variable_name}`: "
        + styled_text(f"{type(variable)}", color=TextColor.ERROR)
    )


def pretty_print(
    text: str,
    color: TextColor | Sequence[TextColor] | None = None,
    style: TextStyle | Sequence[TextStyle] | None = None,
) -> None:
    """Pretty print the text given. Formats the entire text string with the
    color/style given.

    Parameters
    ----------
    color: TextColor | Sequence[TextColor] | None = None,
        The color for the text. This should be a member of the TextColor enum
        or it should be a Sequence of TextColor members.

    style: TextStyle | Sequence[TextStyle] | None = None,
        The style for the text. This should be a member of the TextStyle enum
        or it should be a Sequence of TextStyle members.

    Example
    -------
    >>> pretty_print("some text that is colored red.", color=TextColor.RED)
    """
    ansi_code = _get_ANSI_escape_code(color=color, style=style)
    styled_string = f"{ansi_code}{text}{RESET}"
    print(styled_string)
    return
