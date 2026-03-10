/* 
Problem Link: https://codeforces.com/group/MWSDmqGsZm/contest/219158/problem/Y

inp: 434500145 147276606 217842775 236387740 op: 00
792319479 461799503 958902232 930755956 op: 04
*/

#include<iostream>
using namespace std;

int main(){
    long long a,b,c,d, res;
    cin >> a >> b >> c >> d;
    res = a % 100;
    res = (res * (b % 100)) % 100;
    res = (res * (c % 100)) % 100;
    res = (res * (d % 100)) % 100;
    if (res < 10){
        cout << "0" << res;
    }else {
        cout << res;
    }
    
}