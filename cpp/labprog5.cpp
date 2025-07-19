#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 100

void insertBinaryTree(int tree[MAX_SIZE], int element) {
    int currentIndex, i;

    if (tree[0] == 0) { // Use 0 to represent an empty value
        tree[0] = element;
        return;
    }

    currentIndex = 0;
    while (tree[currentIndex] != 0) {
        if (element < tree[currentIndex])
            currentIndex = 2 * currentIndex + 1;
        else
            currentIndex = 2 * currentIndex + 2;
    }

    tree[currentIndex] = element; // Simplified assignment

    printf("Constructed Binary Tree:\n");
    for (i = 0; i < MAX_SIZE; i++) {
        if (tree[i] != 0)
            printf("tree[%d] => %d\n", i, tree[i]);
    }
}

int main() {
    int numberOfElements, tree[MAX_SIZE], i, element;

    for (i = 0; i < MAX_SIZE; i++)
        tree[i] = 0; // Initialize array with 0s

    printf("Enter the number of elements to insert into the Binary Tree:\n");
    scanf("%d", &numberOfElements);

    printf("Enter the elements to insert into the Binary Tree:\n");
    for (i = 0; i < numberOfElements; i++) {
        scanf("%d", &element);
        insertBinaryTree(tree, element);
    }

    return 0;
}
