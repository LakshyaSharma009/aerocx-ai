#include <stdio.h>
#include <string.h>
#define size 5

int sender(int *, int *, char [][100], int *);
int receiver(int *, int *, char [][100], int *);
int display(int, int, char [][100], int);

int main() {
    int rear = -1, front = 0, isEmpty = 1, ch;
    char queue[size][100];

    while (1) {
        printf("\n1: Send Message  2: Receive Message  3: Display Messages  4: Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &ch);

        switch (ch) {
            case 1:
                sender(&front, &rear, queue, &isEmpty);
                break;
            case 2:
                receiver(&front, &rear, queue, &isEmpty);
                break;
            case 3:
                display(front, rear, queue, isEmpty);
                break;
            case 4:
                printf("Exiting program...\n");
                return 0;
            default:
                printf("Enter a valid choice.\n");
        }
    }
}

int sender(int *front, int *rear, char queue[][100], int *isEmpty) {
    char message[100];
    if (*front == ((*rear + 1) % size) && *isEmpty == 0) {
        printf("Queue is full\n");
    } else {
        printf("Enter the message to send: ");
        scanf(" %[^\n]", message);

        *rear = (*rear + 1) % size;
        strcpy(queue[*rear], message);
        *isEmpty = 0; // Queue is no longer empty

        printf("Message '%s' sent.\n", message);
    }
    return 0;
}

int receiver(int *front, int *rear, char queue[][100], int *isEmpty) {
    if (*isEmpty) {
        printf("The queue is empty, no message to receive.\n");
    } else {
        printf("Message received: %s\n", queue[*front]);

        if (*front == *rear) { // Reset queue when the last element is removed
            *front = 0;
            *rear = -1;
            *isEmpty = 1; // Queue is now empty
        } else {
            *front = (*front + 1) % size;
        }
    }
    return 0;
}

int display(int front, int rear, char queue[][100], int isEmpty) {
    if (isEmpty) {
        printf("The queue is empty\n");
    } else {
        printf("Messages in the queue:\n");
        int i = front;
        do {
            printf("%s\n", queue[i]);
            i = (i + 1) % size;
        } while (i != (rear + 1) % size);
    }
    return 0;
}
