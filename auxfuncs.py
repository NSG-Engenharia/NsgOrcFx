
def isConnectedToObj(connection: str) -> bool:
    """Returns true if the connection refers to other object"""
    if connection == 'Free' or connection == 'Fixed' or connection == 'Anchored':
        return False
    else:
        return True

def compareStrings(
        strA: str, 
        strB: str, 
        partialMatch: bool=False
        ) -> bool:
    if partialMatch:
        n = min(len(strA), len(strB))
        strA = strA[:n]
        strB = strB[:n]    
    # print(f'strA={strA} | strB={strB}')
    return strA == strB

def strInStrList(
        str: str,
        strList: list[str],
        partialMatch: bool=False
        ) -> bool:    
    for s in strList:
        if compareStrings(s, str, partialMatch): return True
    return False
