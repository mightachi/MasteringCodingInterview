/*
Problem set: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/R
*/
#include<iostream>
using namespace std;

int main(){
    int age;
    cin >> age;
    cout << age/365 << " years" << endl;
    age = age%365;
    cout << age/30 << " months" << endl;
    age = age%30;
    cout << age << " days";
}