# Used since at main, see config.py etc.


def password(uid, time=None, *, test_mode=False) -> 'typing.Optional[str]':
    """Generate a password. Depends on time. Optionally, can choose time."""
    import datetime  # *Only* locally used.

    now = datetime.datetime.now()

    if time is not None:
        max_delta = 3*60

        def number(s: str) -> int:
            # '0..0number' -> number: int
            zero = '0'
            return int(_res) if (_res := s.lstrip(zero)) else 0

        minute, second = map(number, time)
        res_date = now.replace(  # timedelta
            minute=minute, second=second)
        # Not to let the password being static:
        if not abs(
            (res_date - now).total_seconds()
        ) < max_delta and not test_mode:
            return
        now = res_date

    secret_code = get('SECRET_CODE')
    if not secret_code:
        return

    time_format = eval(get("SECRET_TIME_FORMAT"))
    big_h, big_m, big_s, d, m, big_y = map(
        int,
        now.strftime(time_format).split()
    )
    res_0 = eval(secret_code).split(',')
    space = {
        'H': big_h,
        'M': big_m,
        'S': big_s,
        'd': d,
        'm': m,
        'Y': big_y,
        'uid': int(uid)
    }

    res_1 = map(lambda i: eval(i, globals(), space), res_0)
    res_2 = list(res_1)
    _res = [str(int(item)) for item in res_2]
    s: int = int(eval(get('SECRET_S')))
    res: str = ("".join(_res)[::s]*2)[:7]

    if __name__ == '__main__':
        print(res)  # Test
    else:
        return res
