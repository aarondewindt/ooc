class KeyPairDictionary(dict):
    """
    Dictionary that uses a tuple with two elements as it's key. The order
    of the pair is ignored.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        if item in self.keys():
            return super().__getitem__(item)
        elif (item[1], item[0]) in self.keys():
            return super().__getitem__((item[1], item[0]))
        raise KeyError()

    def __setitem__(self, key, value):
        if (key[1], key[0]) in self.keys():
            return super().__setitem__((key[1], key[0]), value)
        else:
            return super().__setitem__(key, value)

    def __contains__(self, item):
        if item in self.keys():
            return True
        elif (item[1], item[0]) in self.keys():
            return True
        return False

    def pairs(self, i):
        """
        Yield all pairs of i

        :param i:
        :return:
        """
        for key in self.keys():
            if i in key:
                yield key[not key.index(i)]

    def contains(self, i):
        for key in self.keys():
            if i in key:
                return True
        return False
