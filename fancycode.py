

class FancyTuple:
    def __init__(self, first=None, second=None, third=None, fourth=None, fifth=None):
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth

    def __getattribute__(self, attr):
        temp = object.__getattribute__(self, attr)
        if temp == None:
            raise AttributeError()
        else:
            return temp

    def __getattr__(self, attr):
        raise AttributeError()

    def __len__(self):
        count = 0
        try:

            if self.first:
                count += 1

            if self.second:
                count += 1

            if self.third:
                count += 1

            if self.fourth:
                count += 1

            if self.fifth:
                count += 1

        except AttributeError:
            return count

# if __name__ == '__main__':
#     print(FancyTuple(1,2,3).second)
#     print(FancyTuple(1,2,3).third)
#     # print(FancyTuple(1,2,3).fourth)
#     print(len(FancyTuple(1,2,3,4)))

