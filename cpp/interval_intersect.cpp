#include<iostream>
#include<cassert>
#include<algorithm>
#include<vector>
#include<tuple>

using namespace std;

typedef vector<pair<int, int> > times_t;

class PairCompare {
public:
    bool operator()(const pair<int, int>& lhs, const pair<int, int>& rhs) {
        return lhs.first < rhs.first;
    }
};

times_t condense_times(times_t& meetings) {
    times_t condensed;

    if (meetings.empty()) {
        return condensed;   
    }

    sort(meetings.begin(), meetings.end());
    
    int prev_start = meetings[0].first;
    int prev_end = meetings[0].second;

    for (int i = 1; i < meetings.size(); ++i) {
        int curr_start = meetings[i].first;
        int curr_end = meetings[i].second;

        if (curr_start <= prev_end) {
            prev_end = max(prev_end, curr_end);
        }
        else {
            condensed.push_back(pair<int, int>(prev_start, prev_end));
            prev_start = curr_start;
            prev_end = curr_end;
        }
    }
    condensed.push_back(pair<int, int>(prev_start, prev_end));
    

    return condensed;
}

bool isEqual(const times_t& l, const times_t& r) {
    if (l.size() != r.size()) {
        return false;
    }

    for (int i = 0; i < l.size(); ++i) {
        if (l[i].first != r[i].first || l[i].second != r[i].second) {
            return false;
        }
    }

    return true;
}

void print_times(const times_t& times) {
    cout << "[";
    for (int i = 0; i < times.size() - 1; ++i) {
        cout << "(" << times[i].first << "," << times[i].second << "), ";
    }
    cout << "(" << times[times.size() - 1].first;
    cout << "," << times[times.size() - 1].second << ")]\n";
}

int main() {
    times_t meetings1 = {pair<int, int>(0, 1),
                         pair<int, int>(3, 5),
                         pair<int, int>(4, 8),
                         pair<int, int>(10, 12),
                         pair<int, int>(9, 10)};
    times_t solution1 = {pair<int, int>(0, 1),
                         pair<int, int>(3, 8),
                         pair<int, int>(9, 12)};

    times_t meetings2 = {pair<int, int>(0, 1),
                         pair<int, int>(3, 4),
                         pair<int, int>(5, 8),
                         pair<int, int>(11, 12),
                         pair<int, int>(9, 10)};
    times_t solution2 = {pair<int, int>(0, 1),
                         pair<int, int>(3, 4),
                         pair<int, int>(5, 8),
                         pair<int, int>(9, 10),
                         pair<int, int>(11, 12)};

    times_t meetings3 = {pair<int, int>(4, 5),
                         pair<int, int>(1, 10)};
    times_t solution3 = {pair<int, int>(1, 10)};

    times_t condensed1 = condense_times(meetings1);
    assert(isEqual(condensed1, solution1));

    times_t condensed2 = condense_times(meetings2);
    assert(isEqual(condensed2, solution2));

    times_t condensed3 = condense_times(meetings3);
    assert(isEqual(condensed3, solution3));

    return 0;
}
