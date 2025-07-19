#include <iostream>
#include <vector>
using namespace std;

void maximumOvertakes(int n, vector<int>& final_order) {
    vector<pair<int, int>> overtakes; // Store overtaking events
    vector<int> current_order(n);    // Initialize the current order of cars
    
    // Initial order of cars is [1, 2, ..., n]
    for (int i = 0; i < n; ++i) {
        current_order[i] = i + 1;
    }
    
    // Simulate overtakes to transform initial order to final order
    for (int i = 0; i < n; ++i) {
        for (int j = i; j > 0; --j) {
            // If the current car is out of place, perform an overtake
            if (final_order[j] < final_order[j - 1]) {
                overtakes.push_back({final_order[j], final_order[j - 1]});
                // Swap the cars in final_order to simulate the overtake
                swap(final_order[j], final_order[j - 1]);
            }
        }
    }
    
    // Output the results
    cout << overtakes.size() << endl;
    for (auto& o : overtakes) {
        cout << o.first << " " << o.second << endl;
    }
}

int main() {
    int n;
    cin >> n; // Number of cars
    vector<int> final_order(n);
    
    // Input the final order of cars
    for (int i = 0; i < n; ++i) {
        cin >> final_order[i];
    }
    
    // Solve the problem
    maximumOvertakes(n, final_order);
    
    return 0;
}
