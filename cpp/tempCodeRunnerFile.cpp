/*
Problem Link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/H
*/

#include<iostream>
#include<cmath>
using namespace std;
int main() {
    float a,b;
    cin >> a >> b;
    cout << "floor "<<a<<" / "<<b<<" = " << floor(a/b) << endl;
    cout << "ceil "<<a<<" / "<<b<<" = " << ceil(a/b) << endl;
    cout << "round "<<a<<" / "<<b<<" = " << round(a/b) << endl;
}