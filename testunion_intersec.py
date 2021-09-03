import datetime

def _union(interv1: list, interv2: list):
    if interv2[0] < interv1[0]:
        interv1, interv2 = interv2, interv1
    if interv1[-1] < interv2[0]:
        return [interv1, interv2]
    if interv2[0] > interv1[0] and interv2[-1] < interv1[-1]:
        return [interv1,]
    return [[interv1[0], interv2[-1]],]


def _inter(interv1: list, interv2: list):
    if interv2[0] < interv1[0]:
        interv1, interv2 = interv2, interv1
    if interv1[-1] < interv2[0]:
        return None
    if interv2[0] > interv1[0] and interv2[-1] < interv1[-1]:
        return interv2
    return [interv2[0], interv1[-1]]

def union(interv_set: list):
    for i in range(len(interv_set) - 1):
        for j in range(i + 1, len(interv_set)):
            if _inter(interv_set[i], interv_set[j]) is not None:
                interv1 = interv_set.pop(i)
                interv2 = interv_set.pop(j-1)
                interv_set.extend(_union(interv1, interv2))
                return union(interv_set)
    return interv_set


def inter(interv_set: list):
    for i in range(len(interv_set) - 1):
        for j in range(i + 1, len(interv_set)):
            intersection = _inter(interv_set[i], interv_set[j])
            if intersection is not None:
                interv1 = interv_set.pop(i)
                interv2 = interv_set.pop(j - 1)
                interv_set.append(_inter(interv1, interv2))
                return inter(interv_set)
            else:
                return None
    return interv_set

if __name__ == '__main__':
    print(union([[1,2], [3,4]]))
    print(union([[1,4], [2,3]]))
    print(union([[1,3], [2,4]]))
    print(union([[1,2], [1, 2]]))
    print(union([[1, 3], [2, 5], [4, 6]]))
    print(union([[1, 3], [2, 5], [4, 6], [8, 10], [11, 14], [11, 15]]))

    print(union([[datetime.datetime(2015, 12, 17, 21, 46, 14), datetime.datetime(2015, 12, 18, 2, 1, 17)],[datetime.datetime(2015, 12, 20, 22, 9, 6), datetime.datetime(2015, 12, 21, 2, 1, 22)]]))

    print(inter([[1,2], [3,4]]))
    print(inter([[1,4], [2,3]]))
    print(inter([[1,3], [2,4]]))
    print(inter([[1,2], [1, 2]]))
    print(inter([[1, 3], [2, 5], [4, 6]]))
    print(inter([[1, 3], [2, 5], [4, 6], [8, 10], [11, 14], [11, 15]]))
    print(inter([[1, 6], [2,7], [-1,9], [3,5]]))