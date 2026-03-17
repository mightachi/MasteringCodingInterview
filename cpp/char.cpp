/*
Note:

Digits in ASCII '0' = 48,'1' = 49 ....etc
Capital letters in ASCII 'A' = 65, 'B' = 66 ....etc
Small letters in ASCII 'a' = 97,'b' = 98 ....etc

difference between 'a' and 'A' in ASCII is 32 .
*/

#include<iostream>
using namespace std;

int main(){
    char x;
    cin >> x;

    if (x >= 'A' and x <= 'Z'){
        cout << char('a' + (x - 'A'));
    }else if (x >= 'a' and x <= 'z'){
        cout << char('A' + (x - 'a'));
    }
}
