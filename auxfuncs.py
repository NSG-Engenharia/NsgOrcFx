def isConnectedToObj(connection: str) -> bool:
    """Returns true if the connection refers to other object"""
    if connection == 'Free' or connection == 'Fixed' or connection == 'Anchored':
        return False
    else:
        return True
