#include <stdio.h>
#include <stdlib.h>

#define NULL 0

struct node {
    int info;
    struct node *llink;
    struct node *rlink;
};

typedef struct node *NODE;

// Function declarations
NODE getnode();
NODE insert_front(int, NODE);
NODE insert_rear(int, NODE);
NODE insert_pos(int, int, NODE);
NODE delete_front(NODE);
NODE delete_rear(NODE);
NODE display(NODE);
NODE search(NODE);
NODE insert_before_val(int, NODE);
int count(NODE);

int main() {
    int item, ch, pos;
    NODE head = NULL;
    
    while (1) {
        printf("\n1: Insert at front\n2: Insert at end\n3: Insert at position\n");
        printf("4: Display\n5: Delete from front\n6: Delete from end\n");
        printf("7: Count nodes\n8: Search\n9: Insert before value\n0: Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &ch);

        switch (ch) {
            case 1:
                printf("Enter the element: ");
                scanf("%d", &item);
                head = insert_front(item, head);
                break;
            case 2:
                printf("Enter the element: ");
                scanf("%d", &item);
                head = insert_rear(item, head);
                break;
            case 3:
                printf("Enter the element: ");
                scanf("%d", &item);
                printf("Enter the position: ");
                scanf("%d", &pos);
                head = insert_pos(item, pos, head);
                break;
            case 4:
                head = display(head);
                break;
            case 5:
                head = delete_front(head);
                break;
            case 6:
                head = delete_rear(head);
                break;
            case 7:
                printf("Number of nodes: %d\n", count(head));
                break;
            case 8:
                head = search(head);
                break;
            case 9:
                printf("Enter the value to insert before: ");
                scanf("%d", &item);
                head = insert_before_val(item, head);
                break;
            case 0:
                exit(0);
            default:
                printf("Invalid choice, try again.\n");
        }
    }
    return 0;
}

NODE getnode() {
    NODE p = (NODE)malloc(sizeof(struct node));
    if (p == NULL) {
        printf("Memory allocation failed.\n");
        exit(1);
    }
    return p;
}

NODE insert_front(int x, NODE head) {
    NODE temp = getnode();
    temp->info = x;
    temp->llink = NULL;
    temp->rlink = head;

    if (head != NULL) {
        head->llink = temp;
    }
    head = temp;

    return head;
}

NODE insert_rear(int x, NODE head) {
    NODE temp = getnode();
    temp->info = x;
    temp->llink = temp->rlink = NULL;

    if (head == NULL) {
        return temp;
    }

    NODE p = head;
    while (p->rlink != NULL) {
        p = p->rlink;
    }
    p->rlink = temp;
    temp->llink = p;

    return head;
}

NODE insert_pos(int x, int pos, NODE head) {
    NODE temp = getnode();
    temp->info = x;
    temp->llink = temp->rlink = NULL;

    if (pos == 1) {
        return insert_front(x, head);
    }

    NODE cur = head;
    for (int i = 1; i < pos - 1 && cur != NULL; i++) {
        cur = cur->rlink;
    }

    if (cur == NULL) {
        printf("Position out of bounds\n");
        free(temp);
        return head;
    }

    temp->rlink = cur->rlink;
    temp->llink = cur;
    if (cur->rlink != NULL) {
        cur->rlink->llink = temp;
    }
    cur->rlink = temp;

    return head;
}

NODE delete_front(NODE head) {
    if (head == NULL) {
        printf("List is empty.\n");
        return head;
    }

    NODE temp = head;
    printf("Deleted node: %d\n", temp->info);

    head = head->rlink;
    if (head != NULL) {
        head->llink = NULL;
    }

    free(temp);
    return head;
}

NODE delete_rear(NODE head) {
    if (head == NULL) {
        printf("List is empty.\n");
        return head;
    }

    NODE cur = head;
    while (cur->rlink != NULL) {
        cur = cur->rlink;
    }

    printf("Deleted node: %d\n", cur->info);

    if (cur->llink != NULL) {
        cur->llink->rlink = NULL;
    } else {
        head = NULL;
    }

    free(cur);
    return head;
}

NODE display(NODE head) {
    if (head == NULL) {
        printf("The list is empty.\n");
        return head;
    }

    NODE cur = head;
    printf("List contents:\n");
    while (cur != NULL) {
        printf("%d ", cur->info);
        cur = cur->rlink;
    }
    printf("\n");

    return head;
}

NODE search(NODE head) {
    int val;
    printf("Enter the value to search: ");
    scanf("%d", &val);

    NODE cur = head;
    while (cur != NULL) {
        if (cur->info == val) {
            printf("Node with value %d found.\n", val);
            return head;
        }
        cur = cur->rlink;
    }

    printf("Node with value %d not found.\n", val);
    return head;
}

NODE insert_before_val(int item, NODE head) {
    int val;
    printf("Enter the value to insert before: ");
    scanf("%d", &val);

    NODE cur = head;
    while (cur != NULL && cur->info != val) {
        cur = cur->rlink;
    }

    if (cur == NULL) {
        printf("Node with value %d not found.\n", val);
        return head;
    }

    NODE temp = getnode();
    temp->info = item;
    temp->llink = cur->llink;
    temp->rlink = cur;

    if (cur->llink != NULL) {
        cur->llink->rlink = temp;
    } else {
        head = temp;
    }
    cur->llink = temp;

    return head;
}

int count(NODE head) {
    int c = 0;
    NODE cur = head;
    while (cur != NULL) {
        c++;
        cur = cur->rlink;
    }
    return c;
}
