#include<iostream>
#include<cassert>
#include<vector>

using namespace std;

void print_ways(const vector<int>& denominations) {
    cout << "[ ";
    for (int i = 0; i < denominations.size() - 1; ++i) {
        cout << denominations[i] << ", ";
    }
    cout << denominations[denominations.size() - 1] << " ]\n";
}

int make_change(int amount, vector<int>& denominations) {
    //Create a memo to hold previous ways of making change
    vector<int> ways_to_make_change(amount + 1);
    ways_to_make_change[0] = 1;

    //Iterate through coins
    for (int i = 0; i < denominations.size(); ++i) {
        int coin = denominations[i];

        //Calculate possible ways with amount left after subtracting a coin
        for (int next_amount = coin; next_amount < amount + 1; ++next_amount) {
            int remaining = next_amount - coin;
            ways_to_make_change[next_amount] += ways_to_make_change[remaining];
        }
    }

    return ways_to_make_change[amount];
}

int main() {
    int amount1 = 5;
    vector<int> denominations1{1, 3, 5};
    int solution1 = 3;

    int amount2 = 4;
    vector<int> denominations2{1, 2, 3};
    int solution2 = 4;

    int amount3 = 0;
    vector<int> denominations3{1, 5, 10};
    int solution3 = 1;

    int possibilities1 = make_change(amount1, denominations1);
    assert(possibilities1 == solution1);

    int possibilities2 = make_change(amount2, denominations2);
    assert(possibilities2 == solution2);

    int possibilities3 =  make_change(amount3, denominations3);
    assert(possibilities3 == solution3);

    return 0;
}
