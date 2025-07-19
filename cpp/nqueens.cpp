#include <stdio.h>
#include <math.h>

int board[20], count = 0;

int isSafe(int row) {
    for (int i = 1; i < row; i++) {
        if (board[i] == board[row] || abs(board[i] - board[row]) == abs(i - row))
            return 0;
    }
    return 1;
}

void printSolution(int n) {
    count++;
    printf("\nSolution #%d:\n", count);
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++)
            printf("%s\t", board[i] == j ? "Q" : "*");
        printf("\n");
    }
}

void solveNQueens(int n) {
    int row = 1;
    board[row] = 0;

    while (row > 0) {
        board[row]++;
        while (board[row] <= n && !isSafe(row))
            board[row]++;
        if (board[row] <= n) {
            if (row == n)
                printSolution(n);
            else {
                row++;
                board[row] = 0;
            }
        } else {
            row--;
        }
    }
}

int main() {
    int n;
    printf("Enter number of queens: ");
    scanf("%d", &n);
    solveNQueens(n);
    printf("\nTotal solutions = %d\n", count);
    return 0;
}
