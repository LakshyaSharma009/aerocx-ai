#include<iostream>
#include<unordered_set>
using namespace std;

void printUnion(int arr[], int brr[], int sizea, int sizeb) {
    // Create a set to store unique elements
    unordered_set<int> unionSet;

    // Insert elements of the first array into the set
    for(int i = 0; i < sizea; i++) {
        unionSet.insert(arr[i]);
    }

    // Insert elements of the second array into the set
    for(int i = 0; i < sizeb; i++) {
        unionSet.insert(brr[i]);
    }

    // Print the elements of the union set
    cout << "Union of the two arrays: ";
    for(auto element : unionSet) {
        cout << element << " ";
    }
    cout << endl;
}

int main() {
    int arr[] = {1, 2, 3, 1, 2, 5, 4};
    int sizea = sizeof(arr)/sizeof(arr[0]);

    int brr[] = {1, 2, 10};
    int sizeb = sizeof(brr)/sizeof(brr[0]);

    printUnion(arr, brr, sizea, sizeb);

    return 0;
}
