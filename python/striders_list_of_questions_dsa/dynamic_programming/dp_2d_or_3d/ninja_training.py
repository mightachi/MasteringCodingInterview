def solve(day:int, last:int, points:list[list], dp: list[list]) -> int:
	if dp[day][last] != -1:
		return dp[day][last]
	if day==0:
		maxi = 0
		for i in range(3):
			if last != i:
				maxi = max(maxi, points[0][i])
		dp[day][last] = maxi
		return dp[day][last]
	maxi = 0
	for i in range(3):
		if  i!= last:
			activity = points[day][i] + solve(day-1, i, points, dp)
			maxi = max(maxi, activity)
	dp[day][last] = maxi
	return maxi

def tab_solve(n:int, points:list[list]) -> int:
	dp = [[0 for _ in range(4)] for i in range(n)]
	
	# Base Condition
	dp[0][0] = max(points[0][1], points[0][2])
	dp[0][1] = max(points[0][0], points[0][2])
	dp[0][2] = max(points[0][0], points[0][1])
	dp[0][3] = max(points[0][0], points[0][1], points[0][2])

	for day in range(1, n):
		for last in range(4):
			dp[day][last] = 0
			for task in range(3):
				if task != last:
					activity = points[day][task] + dp[day-1][task]
					dp[day][last] = max(dp[day][last], activity)
	return dp[n-1][3]

def so_solve(n:int, points: list[list]) -> int:
	prev = [0] * 4
	prev[0] = max(points[0][1], points[0][2])
	prev[1] = max(points[0][0], points[0][2])
	prev[2] = max(points[0][0], points[0][1])
	prev[3] = max(points[0][0], max(points[0][1], points[0][2]))

	for day in range(1, n):
		temp = [0] * 4
		for last in range(4):
			temp[last] = 0
			for task in range(3):
				if last != task:
					activity = points[day][task] + prev[task]
					temp[last] = max(temp[last], activity)
		prev = temp
	return prev[3]




if __name__ == "__main__":
	points = [[10, 40, 70],
				[20, 50, 80],
				[30, 60, 90]]

	n = len(points)  # Get the number of days.
	# Call the ninjaTraining function to find the maximum points.

	dp = [[-1 for j in range(4)] for i in range(n)]
	print(solve(n-1, 3, points, dp))

	print(tab_solve(n, points))
	print(so_solve(n, points))
	