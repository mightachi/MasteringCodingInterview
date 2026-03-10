/*
Problem Link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/L
*/

#include<iostream>
#include<string>

using namespace std;

int main() {
    std::string f1, s1, f2, s2;
    std::cin >> f1 >> s1 >> f2 >> s2;
    if (s1 == s2){
        std::cout << "ARE Brothers" << endl;
    }else {
        std::cout << "NOT" << endl;
    }
}