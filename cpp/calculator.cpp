/*
problem link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/O
*/

#include<iostream>
#include<string>
using namespace std;

int main(){
    char x[10];
    int a,b;
    char s;
    cin >> a >> s >> b;
    if (s=='+'){
        cout << a + b;
    }else if(s=='-'){
        cout << a - b;
    }else if(s=='*'){
        cout << a * b;
    }else {
        cout << a/b;
    }
}