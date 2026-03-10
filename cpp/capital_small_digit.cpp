/*
Problem Link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/M
*/

#include<iostream>
using namespace std;

int main(){
    char x;
    cin >> x;
    if (x>='0' and x<='9'){
        cout << "IS DIGIT";
    } else if (x>='A' and x<='Z'){
        cout << "ALPHA" << endl << "IS CAPITAL";
    } else if (x>='a' and x<='z'){
        cout << "ALPHA" << endl << "IS SMALL";
    }
}