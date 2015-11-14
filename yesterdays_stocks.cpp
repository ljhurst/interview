#include<iostream>
#include<vector>
#include<cassert>

using namespace std;

int get_max_profit(vector<int>& prices) {
    //Ensure there are at least two prices
    if (prices.size() < 2) {
        cerr << "Require at least two prices to calculate a profit" << endl;
        exit(0);
    }

    //Initialize maximum profit
    int max_profit = prices[1] - prices[0];
    //Initialize minimum price
    int min_price = prices[0];

    for (int i = 1; i < prices.size(); ++i) {
        //If the current price minus the min price has a larger profit, use it
        int current_profit = prices[i] - min_price;
        if (current_profit > max_profit) {
            max_profit =  current_profit;
        }

        //If the current price is less than the minimum price, use it
        int current_price = prices[i];
        if (current_price < min_price) {
            min_price = current_price;
        }
    }

    return max_profit;
}

int main() {
    //Initialize lists for testing
    vector<int> yesterdays_prices1 = {10, 7, 5, 8, 11, 9};
    vector<int> yesterdays_prices2 = {5, 5, 5, 5};
    vector<int> yesterdays_prices3 = {10, 9, 8, 7, 6, 5};

    int profit;

    //Find the maximum profit in a list of varying prices
    profit = get_max_profit(yesterdays_prices1);
    assert(profit == 6);

    //Find the maximum profit in a list of constant prices
    profit = get_max_profit(yesterdays_prices2);
    assert(profit == 0);

    //Find the maximum profit in a list of decreasing prices
    profit = get_max_profit(yesterdays_prices3);
    assert(profit == -1);

    return 0;
}
