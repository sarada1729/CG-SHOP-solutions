def subsets(S,i):
    if i==0:return {frozenset(S)}
    else:return frozenset((subsets(S,i-1)).subsets(S.union({i}),i-1))
S={0,1,2,3}
print(subsets(S,3))