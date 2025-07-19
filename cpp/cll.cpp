#include <stdio.h>
#include <stdlib.h>

#define NULL  '\0'

struct node {
    int info;
    struct node *ptr;
};

typedef struct node *NODE;

// Function Prototypes
NODE insert_front(int, NODE);
NODE insert_rear(int, NODE);
NODE insert_pos(int, int, NODE);
NODE delete_front(NODE);
NODE delete_rear(NODE);
void display(NODE);
int count_nodes(NODE);
NODE getnode();

// Main Function
int main() {
    int item, ch, pos;
    NODE start = NULL;

    while (1) {
        printf("\n1: Insert front \n2: Insert at End \n3: Insert at Position \n");
        printf("4: Display \n5: Delete from Front \n6: Delete from End \n7: Count Nodes \n");
        printf("8: Exit\n");
        scanf("%d", &ch);

        switch (ch) {
            case 1:
                printf("Enter the element: ");
                scanf("%d", &item);
                start = insert_front(item, start);
                break;
            case 2:
                printf("Enter the element: ");
                scanf("%d", &item);
                start = insert_rear(item, start);
                break;
            case 3:
                printf("Enter the element: ");
                scanf("%d", &item);
                printf("Enter the position: ");
                scanf("%d", &pos);
                start = insert_pos(item, pos, start);
                break;
            case 4:
                display(start);
                break;
            case 5:
                start = delete_front(start);
                break;
            case 6:
                start = delete_rear(start);
                break;
            case 7:
                printf("The number of nodes is %d\n", count_nodes(start));
                break;
            case 8:
                exit(0);
            default:
                printf("Invalid choice\n");
        }
    }

    return 0;
}

// Function Definitions
int count_nodes(NODE start) {
    if (start == NULL) {
        printf("The list is empty\n");
        return 0;
    }

    int count = 1;
    NODE temp = start;
    while (temp->ptr != start) {
        count++;
        temp = temp->ptr;
    }
    return count;
}

NODE getnode() {
    NODE p = (NODE)malloc(sizeof(struct node));
    if (p == NULL) {
        printf("Memory allocation failed\n");
        exit(1);
    }
    return p;
}

NODE insert_front(int x, NODE start) {
    NODE temp = getnode();
    temp->info = x;
    temp->ptr = temp;

    if (start == NULL) {
        return temp;
    }

    NODE p = start;
    while (p->ptr != start) {
        p = p->ptr;
    }
    p->ptr = temp;
    temp->ptr = start;
    return temp;
}

void display(NODE start) {
    if (start == NULL) {
        printf("The list is empty\n");
        return;
    }

    NODE cur = start;
    printf("The contents of the list are:\nStart");
    do {
        printf(" => %d ", cur->info);
        cur = cur->ptr;
    } while (cur != start);
    printf("\n");
}

NODE insert_rear(int x, NODE start) {
    NODE temp = getnode();
    temp->info = x;
    temp->ptr = temp;

    if (start == NULL) {
        return temp;
    }

    NODE cur = start;
    while (cur->ptr != start) {
        cur = cur->ptr;
    }
    cur->ptr = temp;
    temp->ptr = start;
    return start;
}

NODE insert_pos(int x, int pos, NODE start) {
    NODE temp = getnode();
    temp->info = x;
    temp->ptr = temp;

    if (pos <= 1 || start == NULL) {
        return insert_front(x, start);
    }

    NODE cur = start;
    int count = 1;
    while (count < pos - 1 && cur->ptr != start) {
        cur = cur->ptr;
        count++;
    }
    temp->ptr = cur->ptr;
    cur->ptr = temp;
    return start;
}

NODE delete_front(NODE start) {
    if (start == NULL) {
        printf("The list is empty\n");
        return NULL;
    }

    if (start->ptr == start) {
        printf("The deleted node is %d\n", start->info);
        free(start);
        return NULL;
    }

    NODE cur = start;
    while (cur->ptr != start) {
        cur = cur->ptr;
    }

    NODE temp = start;
    start = start->ptr;
    cur->ptr = start;
    printf("The deleted node is %d\n", temp->info);
    free(temp);

    return start;
}

NODE delete_rear(NODE start) {
    if (start == NULL) {
        printf("The list is empty\n");
        return NULL;
    }

    if (start->ptr == start) {
        printf("The deleted node is %d\n", start->info);
        free(start);
        return NULL;
    }

    NODE cur = start;
    NODE prev = NULL;
    while (cur->ptr != start) {
        prev = cur;
        cur = cur->ptr;
    }

    printf("The deleted node is %d\n", cur->info);
    prev->ptr = start;
    free(cur);

    return start;
}