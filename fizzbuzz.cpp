//Programmer: Luke J. Hurst
//Date: November, 2015
//Purpose: This program plays a game of FizzBuzz.
//           If a number is divisible by three, Fizz is printed.
//           If a number is divisible by five, Buzz is printed.
//           If a number is divisible by both, FizzBuzz is printed.
//           Otherwise the number itself is printed.
//         The game is played from 0 to 100


#include<iostream>

using namespace std;

int main() {

    //Iterate through numbers 1 to 100
    for (int i = 1; i <= 100; i++) {
        //If a number is divisible by 3 and 5
        if ((i % 3 == 0) && (i % 5 == 0)) {
            cout << "FizzBuzz\n";
        }
        //If a number is divisible by 3
        else if (i % 3 == 0) {
            cout << "Fizz\n";
        }
        //If a number is divisible by 5
        else if (i % 5 == 0) {
            cout << "Buzz\n";
        }
        //Otherwise
        else {
            cout << i << "\n";
        }
    }

    return 0;
}
