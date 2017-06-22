def pad(string, length, pad=" ", pos=1.0):
    """
    Pads a string to achieve a minimum length.

    @param pad
      The pad character.
    @param pos
      How the pad is split between the ends: 0 for left, 1 for right.
    """
    if not (0 <= pos <= 1):
        raise RangeError("bad pos: {}".format(pos))

    string = str(string)
    if len(string) >= length:
        return string

    pad_len = len(pad)
    add     = length - len(string)
    right   = int(round(pos * add))
    left    = add - right
    if left > 0:
        string = pad * (left // pad_len) + pad[: left % pad_len] + string
    if right > 0:
        string = (
            string 
            + pad[pad_len - (right % pad_len) :] 
            + pad * (right // pad_len)
        )
    return string


_pad = pad


def elide(string, length, ellipsis=u"\u2026", pos=1.0):
    """
    Elides characters if necessary to fit `string` in `length` characters.

    @param ellipsis
      The string to indicate the elided characters.
    @param pos
      The position of the ellipsis: 0 for left, 1 for right.
    """
    if length < len(ellipsis):
        raise ValueError("max_length less than ellipsis length")
    if not (0 <= pos <= 1):
        raise RangeError("bad pos: {}".format(pos))

    string = str(string)
    if len(string) <= length:
        return string

    keep    = length - len(ellipsis)
    left    = int(round(pos * keep))
    right   = keep - left
    return (
          (string[: left] if left > 0 else "")
        + ellipsis
        + (string[-right :] if right > 0 else "")
    )


def palide(string, length, ellipsis=u"\u2026", pad=" ", pad_pos=1.0, 
           elide_pos=1.0):
    """
    A combination of `elide` and `pad`.
    """
    return _pad(
        elide(string, length, ellipsis=ellipsis, pos=elide_pos), 
        length, pad=pad, pos=pad_pos)


