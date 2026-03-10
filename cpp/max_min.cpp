/*
Problem Link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/K
*/
#include<iostream>
using namespace std;

int main(){
    int a,b,c;
    cin >> a >> b >> c;
    // Print the minimum of all three
    if (a<=b and a<=c){
        cout << a;
    }else if (b<=a and b<=c){
        cout << b;
    }else {
        cout << c;
    }
    // Print the maximum
    if (a>=b and a>=c){
        cout << " " << a;
    }else if (b>=c and b>=a){
        cout << " " << b;
    }else {
        cout << " " << c;
    }
}