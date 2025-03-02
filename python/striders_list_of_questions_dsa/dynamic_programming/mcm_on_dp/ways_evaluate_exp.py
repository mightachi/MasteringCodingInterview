def evaluateExp(exp):
    n = len(exp)
    mod = 100000007
    def f(i,j,isTrue,dp):
        if i>j:
            return 0
        if i==j:
            if isTrue==1:
                return exp[i]=="T"
            else:
                return exp[i]=="F"
        if dp[i][j][isTrue] != -1:
            return dp[i][j][isTrue]
        ways = 0
        for k in range(i + 1, j, 2):
            lT = f(i,k-1,1,dp)
            lF = f(i,k-1,0,dp)
            rT = f(k+1,j,1,dp)
            rF = f(k+1,j,0,dp)
            if exp[k] == "&":
                if isTrue:
                    ways = (ways + (lT*rT)%mod)%mod
                else:
                    ways = (ways + (lT*rF)%mod + (lF*rT)%mod + (lF*rF)%mod) % mod
            elif exp[k] == "|":
                if isTrue:
                    ways = (ways + (lT*rF)%mod + (lF*rT)%mod + (lT*rT)%mod) % mod
                else:
                    ways = (ways + (lF*rF)%mod)%mod
            elif exp[k] == "^":
                if isTrue:
                    ways = (ways + (lT*rF)%mod + (lF*rT)%mod)%mod
                else:
                    ways = (ways + (lT*rT)%mod + (lF*rF)%mod)%mod
        dp[i][j][isTrue] = ways
        return ways
    dp = [[[-1 for _ in range(2)] for _ in range (n)] for _ in range(n)]
    return f(0,n-1,1,dp)


if __name__ == "__main__":
    exp = "F|T^F"
    ways = evaluateExp(exp)
    print("The total number of ways:", ways)

