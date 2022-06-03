from datetime import datetime
def getDateTimeObj(dateStr):
    """Convert the string from Microsoft into a usable datetime object"""

    return datetime.strptime(dateStr[:-2] if dateStr.endswith('Z') else dateStr[:-1], "%Y-%m-%dT%H:%M:%S.%f")

def multikeysort(items, columns):
    """
    Return the sorted list of dictionaries 'items' sorted in order by the keys in 'columns'. 
    
    These keys are specified as a list of strings in 'columns'. A '-' can be added to the 
    front of each key to reverse the sort order.
    """

    dueDateKeyString = "dueDateTime"
    modifDateKeyString = "lastModifiedDateTime"
    createDateKeyString = "createdDateTime"
    
    from functools import cmp_to_key
    stripped_cols = [(col[1:].strip(), -1) if col.startswith('-') else
                        (col.strip(), 1) for col in columns]

    def cmp(x, y, str):
        cmpx = x[str]
        cmpy = y[str]
        if(str == modifDateKeyString or str == createDateKeyString):
            return (getDateTimeObj(cmpx) - getDateTimeObj(cmpy)).total_seconds()
        return (cmpx > cmpy) - (cmpx < cmpy)

    def cmp_due_date(x, y, str):
        """Compare the dueDateTime attributes of two list items.
        param x: The first item to compare
        param y: The second item to compare
        param getter: The itemgetter function to use to retrieve the column data
        """

        xDateExists = dueDateKeyString in x.keys()
        yDateExists = dueDateKeyString in y.keys()
        if(xDateExists and yDateExists):
            return (getDateTimeObj(x[str]['dateTime']) - getDateTimeObj(y[str]['dateTime'])).total_seconds()
        elif(xDateExists):
            return -1
        elif(yDateExists):
            return 1
        else:
            return 0

    # Create the itemgetters and append a boolean to use the custom  comparer for the dueDateTime column
    comparers = [(str, mult, cmp_due_date) if str == dueDateKeyString else (str, mult, cmp)
                    for str, mult in stripped_cols]

    def comparer(left, right):
        comparer_iter = (
            cmp_fn(left, right, fn) * mult
            for fn, mult, cmp_fn in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    
    return sorted(items, key=cmp_to_key(comparer))