# A util to form pattern


def iter_possible(word: str, *, maxlength=20):
    def reduce(s, *, obj='*?'):
        if set(obj) == {'*', '?'}:
            _result = s.replace('?*', '*?')
            if _result != s:
                s = _result
                return reduce(s, obj=obj)
            return _result
        elif set(obj) == {'?'}:
            return re.sub(r'\?+', '?', s)
        else:
            raise SyntaxError("developer er.: Undefined `obj` type")
    word = reduce(word)
    word = reduce(word, obj='?')
    def generate_combinations(n, maxsum=None):
        # number of return's object length is less then ~`maxsum**n`
        if n >= 3:
            raise SyntaxError("Not more than 3 `?` are allowed")
        def with_exact_sum(m=None):  # m is sum
            if m == 0:
                yield iter(tuple([0]*n))
            elif m == 1:
                # for i in range(n + 1):
                for i in range(n):
                    yield (i == j for j in range(n))
            else:
                pass
            _combs = ...
            # return

        for k in range(maxsum + 1):
            yield from with_exactly_sum(k)

    word_ = word.split('?')
    _maxlength = maxlength - len(''.join(word_))
    maxlength = max(0, _maxlength)
    maxlength = min(10, maxlength)
    combinations = generate_combinations(len(word_) - 1,
                         maxlength)
    def form_pre_result(comb):
        word_1 = iter(word_)
        # ^ now word_ it an iterator of str
        while True:
            try:
                yield next(word_1)
                yield '*' * next(comb)
            except StopIteration:
                break
    return (''.join(form_pre_result(comb)) for comb in combinations)

''' console outputs
>>> list(iter_possible('ab?c'))
['abc', 'ab*c']
>>> list(iter_possible('ab?c*?*'))
['abc**', 'ab*c**', 'abc***']
'''
