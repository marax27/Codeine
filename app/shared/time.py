from time import time


class TimeProvider:
    '''To all of you wondering what's the reason behind this class:
    using time() alone would work just fine, so why do we need an entire
    new class?
    It will be useful in testing units which are time-dependent.
    If a class has to wait e.g. 10 seconds to perform an action, we can
    just make it *think* that 10 seconds have just passed.
    '''

    def now(self) -> float:
        return time()
