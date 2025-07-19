#include <stdio.h>
#define SIZE 5

int queue[SIZE], front = 0, rear = -1, c = 0;

// Function to insert an element into the queue
void insert(int value) {
    if (c == SIZE) {
        printf("Queue is Full! Cannot insert %d\n", value);
    } else {
        rear = (rear + 1) % SIZE;  // Circular increment for rear
        queue[rear] = value;
        printf("%d inserted into the queue\n", value);
        c++;
    }
}

// Function to delete an element from the queue
void delete() {
    if (c == 0) {
        printf("Queue is Empty! Nothing to delete\n");
    } else {
        printf("%d deleted from the queue\n", queue[front]);
        front = (front + 1) % SIZE;  // Circular increment for front
        c--;
    }
}

// Function to display the elements of the queue
void display() {
    if (c == 0) {
        printf("Queue is Empty!\n");
    } else {
        printf("Queue elements are: \n");
        for (int i = 0; i < c; i++) {
            printf("Queue[%d] = %d\n", (front + i) % SIZE, queue[(front + i) % SIZE]);
        }
        printf("\n");
    }
}

int main() {
    int choice, value;

    while (1) {
        printf("\nQueue Operations:\n");
        printf("1. Insert\n2. Delete\n3. Display\n4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter the value to insert: ");
                scanf("%d", &value);
                insert(value);
                break;
            case 2:
                delete();
                break;
            case 3:
                display();
                break;
            case 4:
                return 0;
            default:
                printf("Invalid choice! Please choose again.\n");
        }
    }
    return 0;
}
