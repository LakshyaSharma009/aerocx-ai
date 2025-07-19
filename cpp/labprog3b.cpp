#include <stdio.h>
#include <stdlib.h>

// Define the structure for a node
struct node {
    int digit;
    struct node *next;
};

typedef struct node *NODE;

// Function to create a new node
NODE createNode(int digit) {
    NODE newNode = (NODE)malloc(sizeof(struct node));
    if (newNode == NULL) {
        printf("Memory allocation failed\n");
        exit(0);
    }
    newNode->digit = digit;
    newNode->next = newNode; // Circular link
    return newNode;
}

// Function to insert a digit at the end of the list
NODE insertEnd(NODE head, int digit) {
    NODE newNode = createNode(digit);
    if (head->next == head) { // List is empty
        head->next = newNode;
        newNode->next = head;
    } else {
        NODE temp = head->next;
        while (temp->next != head) {
            temp = temp->next;
        }
        temp->next = newNode;
        newNode->next = head;
    }
    return head;
}

// Function to add two long integers represented by linked lists
NODE addLongIntegers(NODE head1, NODE head2) {
    NODE resultHead = createNode(0); // Header node for result
    NODE p1 = head1->next;
    NODE p2 = head2->next;
    int carry = 0;

    while (p1 != head1 || p2 != head2 || carry > 0) {
        int sum = carry;
        if (p1 != head1) {
            sum += p1->digit;
            p1 = p1->next;
        }
        if (p2 != head2) {
            sum += p2->digit;
            p2 = p2->next;
        }
        carry = sum / 10;
        sum = sum % 10;
        resultHead = insertEnd(resultHead, sum);
    }

    return resultHead;
}

// Function to print the number represented by the list
void printList(NODE head) {
    if (head->next == head) {
        printf("List is empty\n");
        return;
    }
    NODE temp = head->next;
    while (temp != head) {
        printf("%d", temp->digit);
        temp = temp->next;
    }
    printf("\n");
}

int main() {
    NODE head1 = createNode(0); // Header node for first number
    NODE head2 = createNode(0); // Header node for second number
    NODE resultHead;
    int choice, digit, listChoice, numDigits;

    while (1) {
        printf("\nMenu:\n");
        printf("1. Insert digit into list\n");
        printf("2. Add the two lists\n");
        printf("3. Print lists\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter list number (1 or 2): ");
                scanf("%d", &listChoice);
                printf("Enter the number of digits to insert: ");
                scanf("%d", &numDigits);
                for (int i = 0; i < numDigits; i++) {
                    printf("Enter digit: ");
                    scanf("%d", &digit);
                    if (listChoice == 1) {
                        head1 = insertEnd(head1, digit);
                    } else if (listChoice == 2) {
                        head2 = insertEnd(head2, digit);
                    } else {
                        printf("Invalid list number\n");
                    }
                }
                break;
            case 2:
                resultHead = addLongIntegers(head1, head2);
                printf("Sum: ");
                printList(resultHead);
                break;
            case 3:
                printf("First list: ");
                printList(head1);
                printf("Second list: ");
                printList(head2);
                break;
            case 4:
                exit(0);
            default:
                printf("Invalid choice\n");
        }
    }

    return 0;
}
