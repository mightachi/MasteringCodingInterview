/*
Problem Link: https://www.codingninjas.com/studio/problems/n-forest_6570177?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems
*/

#include <iostream>
using namespace std;

void nForest(int n) {
	// Write your code here.
	for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cout << "*";
        }
        cout << endl;
    }
}

int main()
{
    int N;
    cin >> N;
    nForest(N);
    return 0;
}
