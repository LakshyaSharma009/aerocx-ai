#include<iostream>
#include<unordered_set>
using namespace std;

void printuniqueno(int arr[], int size) {
    unordered_set<int> unique;       // Set to hold unique elements
    unordered_set<int> duplicates;   // Set to hold duplicates

    for(int i = 0; i < size; i++) {
        if(unique.find(arr[i]) == unique.end()) {
            // If element is not found in unique set
            unique.insert(arr[i]);
        } else {
            // If element is found in unique, it's a duplicate
            duplicates.insert(arr[i]);
        }
    }

    // Print elements in unique set that are not in duplicates
    for(auto it = unique.begin(); it != unique.end(); ++it) {
        if(duplicates.find(*it) == duplicates.end()) {
            cout << *it << endl;
        }
    }
}

int main() {
    int arr[] = {1, 2, 3, 1, 2, 5, 4};
    int size = sizeof(arr) / sizeof(arr[0]);

    printuniqueno(arr, size);

    cout << "Size is: " << size << endl;

    // Print array elements
    for(int k = 0; k < size; k++) {
        cout << arr[k] << " ";
    }

    return 0;
}
