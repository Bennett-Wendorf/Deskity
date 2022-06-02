def multikeysort(items, columns):
    """
    Return the sorted list of dictionaries 'items' sorted in order by the keys in 'columns'. 
    
    These keys are specified as a list of strings in 'columns'. A '-' can be added to the 
    front of each key to reverse the sort order.
    """
    
    from operator import itemgetter
    from functools import cmp_to_key
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
                for col in columns]
    def cmp(x, y):
        return (x > y) - (x < y)

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))