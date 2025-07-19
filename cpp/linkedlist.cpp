#include <stdio.h>
#define SIZE 5

int data[SIZE];      // Array to hold data
int next[SIZE];      // Array to hold 'next' pointers
int head = -1;       // Head of the linked list
int freeList = 0;    // Points to the next free index in arrays

// Function to initialize the 'next' array
void initializeFreeList() {
    for (int i = 0; i < SIZE - 1; i++) {
        next[i] = i + 1;
    }
    next[SIZE - 1] = -1;  // Last element in free list points to -1
}

// Function to insert an element at the end of the linked list
void insertEnd(int value) {
    if (freeList == -1) {
        printf("List is full\n");
        return;
    }

    int newIndex = freeList;
    freeList = next[freeList];  // Update freeList to next available position

    data[newIndex] = value;
    next[newIndex] = -1;

    if (head == -1) {
        head = newIndex;
    } else {
        int temp = head;
        while (next[temp] != -1) {
            temp = next[temp];
        }
        next[temp] = newIndex;
    }
}

// Function to display the linked list
void display() {
    if (head == -1) {
        printf("List is empty\n");
        return;
    }

    int temp = head;
    while (temp != -1) {
        printf("%d -> ", data[temp]);
        temp = next[temp];
    }
    printf("NULL\n");
}

int main() {
    initializeFreeList();

    insertEnd(10);
    insertEnd(20);
    insertEnd(30);
    insertEnd(40);
    insertEnd(50);

    printf("Linked List: ");
    display();  // Output: 10 -> 20 -> 30 -> 40 -> 50 -> NULL

    return 0;
}
