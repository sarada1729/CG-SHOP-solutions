def subsets(S,i):
    if i==0:return {frozenset(S)}
    else:return frozenset(subsets(S,i-1).union(frozenset(subsets(S.union({i}),i-1))))
