#include <iostream>
#include <vector>
#include <queue>
using namespace std;

// Structure for heap elements
struct HeapNode {
    int value;      // Value of the element
    int arrayIndex; // Index of array from which element came
    int elementIndex; // Index of element in the array
    
    HeapNode(int val, int arrIdx, int elemIdx) : 
        value(val), arrayIndex(arrIdx), elementIndex(elemIdx) {}
};

// Comparator for min-heap
struct CompareHeapNode {
    bool operator()(const HeapNode& a, const HeapNode& b) {
        return a.value > b.value;
    }
};

// Approach 1: Using Min Heap
vector<int> mergeKSortedArraysHeap(vector<vector<int>>& arrays) {
    vector<int> result;
    
    // Create a min heap
    priority_queue<HeapNode, vector<HeapNode>, CompareHeapNode> minHeap;
    
    // Push first element from each array into the heap
    for (int i = 0; i < arrays.size(); i++) {
        if (!arrays[i].empty()) {
            minHeap.push(HeapNode(arrays[i][0], i, 0));
        }
    }
    
    // Keep popping minimum element and add to result
    while (!minHeap.empty()) {
        HeapNode current = minHeap.top();
        minHeap.pop();
        
        result.push_back(current.value);
        
        // If there are more elements in the array, push next element
        if (current.elementIndex + 1 < arrays[current.arrayIndex].size()) {
            minHeap.push(HeapNode(
                arrays[current.arrayIndex][current.elementIndex + 1],
                current.arrayIndex,
                current.elementIndex + 1
            ));
        }
    }
    
    return result;
}

// Approach 2: Using Divide and Conquer
vector<int> mergeTwoArrays(const vector<int>& arr1, const vector<int>& arr2) {
    vector<int> merged;
    int i = 0, j = 0;
    
    while (i < arr1.size() && j < arr2.size()) {
        if (arr1[i] <= arr2[j]) {
            merged.push_back(arr1[i++]);
        } else {
            merged.push_back(arr2[j++]);
        }
    }
    
    // Add remaining elements
    while (i < arr1.size()) merged.push_back(arr1[i++]);
    while (j < arr2.size()) merged.push_back(arr2[j++]);
    
    return merged;
}

vector<int> mergeKSortedArraysDC(vector<vector<int>>& arrays) {
    if (arrays.empty()) return vector<int>();
    if (arrays.size() == 1) return arrays[0];
    
    vector<int> result = arrays[0];
    for (int i = 1; i < arrays.size(); i++) {
        result = mergeTwoArrays(result, arrays[i]);
    }
    
    return result;
}

int main() {
    // Example usage
    vector<vector<int>> arrays = {
        {1, 4, 7},
        {2, 5, 8},
        {3, 6, 9},
        {0, 10, 11}
    };
    
    // Using Min Heap approach
    cout << "Result using Min Heap:\n";
    vector<int> result1 = mergeKSortedArraysHeap(arrays);
    for (int num : result1) {
        cout << num << " ";
    }
    cout << "\n\n";
    
    // Using Divide and Conquer approach
    cout << "Result using Divide and Conquer:\n";
    vector<int> result2 = mergeKSortedArraysDC(arrays);
    for (int num : result2) {
        cout << num << " ";
    }
    cout << "\n";
    
    return 0;
}
