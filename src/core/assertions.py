class TestAssertionError(AssertionError):
    pass


def check(condition: bool, message: str):
    if not condition:
        raise TestAssertionError(message)
