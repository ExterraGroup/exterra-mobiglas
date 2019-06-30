class SuffixFilter:

    def __init__(self, suffix):
        self.suffix = suffix

    @staticmethod
    def match(suffix, src: bytes):
        if src is None:
            return False
        return src.decode().endswith(suffix)

    @staticmethod
    def find(suffix, lst):
        matched = []
        if lst is None:
            return matched
        for i in lst:
            if SuffixFilter.match(suffix, i):
                matched.append(i.decode())
        return matched


class PrefixFilter:

    @staticmethod
    def match(prefix, src: bytes):
        if src is None:
            return False
        return src.decode().startswith(prefix)

    @staticmethod
    def find(prefix, lst):
        matched = []
        if lst is None:
            return matched
        for i in lst:
            if PrefixFilter.match(prefix, i):
                matched.append(i.decode())
        return matched


class ContainsFilter:

    @staticmethod
    def match(keyword, src: bytes):
        if src is None:
            return False
        return keyword in src

    @staticmethod
    def find(keyword, lst):
        matched = []
        if lst is None:
            return matched
        for i in lst:
            if ContainsFilter.match(keyword, i):
                matched.append(i.decode())
        return matched
