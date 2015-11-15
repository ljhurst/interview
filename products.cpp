#include<iostream>
#include<cassert>
#include<vector>

using namespace std;

vector<int> get_products(vector<int>& integers) {
    vector<int> products = integers;
    int initial_product = 1;

    for (int i = 0; i < integers.size(); ++i) {
       products[i] = initial_product;
       initial_product *= integers[i];
    }

    initial_product = 1;

    for (int i = integers.size() - 1; i > -1; --i) {
        products[i] *= initial_product;
        initial_product *= integers[i];
    }

    return products;
}

bool isEqual(const vector<int>& lhs, const vector<int>& rhs) {
    if (lhs.size() != rhs.size()) {
        return false;
    }

    for (int i = 0; i < lhs.size(); ++i) {
        if (lhs[i] != rhs[i]) {
            return false;
        }
    }

    return true;
}

int main() {
    vector<int> testIntegers1{1, 7, 3, 4};
    vector<int> solutionIntegers1{84, 12, 28, 21};
    vector<int> testIntegers2{1, 2, 6, 5, 9};
    vector<int> solutionIntegers2{540, 270, 90, 108, 60};
    vector<int> testIntegers3{};
    vector<int> solutionIntegers3{};

    vector<int> testProducts1 = get_products(testIntegers1);
    assert(isEqual(solutionIntegers1, testProducts1));

    vector<int> testProducts2 = get_products(testIntegers2);
    assert(isEqual(solutionIntegers2, testProducts2));

    vector<int> testProducts3 = get_products(testIntegers3);
    assert(isEqual(solutionIntegers3, testProducts3));

    return 0;
}
