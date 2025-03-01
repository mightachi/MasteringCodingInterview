def solve(g:list, s:list) -> int:
    g.sort()
    s.sort()
    gind = 0
    sind = 0
    glen = len(g)
    slen = len(s)
    ans = 0
    while sind<slen and gind<glen:
        if s[sind] >= g[gind]:
            sind+=1
            gind+=1
            ans +=1
        else:
            gind+=1
    return ans


if __name__ == "__main__":
    g = [1,2,3]
    s = [1,1]
    print(solve(g,s))