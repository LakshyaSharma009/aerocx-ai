#include<stdio.h> 
#include<string.h> 
#include<ctype.h> 

#define MAX 50

char stack[MAX]; 
int top = -1; 

void push(char x) { 
    if (top == MAX - 1) { 
        printf("Stack overflow\n"); 
        return; 
    } 
    stack[++top] = x; 
} 

char pop() { 
    if (top == -1) { 
        printf("Stack underflow\n"); 
        return '#'; 
    } 
    return stack[top--]; 
} 

int prior(char x) { 
    if (x == '(' || x == '#') return 1;    
    if (x == '+' || x == '-') return 2;  
    if (x == '*' || x == '/') return 3; 
    if (x == '^' || x == '$') return 4;    
    return 0; 
} 

void infixToPostfix(char *infix, char *postfix) { 
    int i, j = 0; 
    push('#'); 
    for (i = 0; i < strlen(infix); i++) { 
        if (isalnum(infix[i])) {   
            postfix[j++] = infix[i]; 
        } else if (infix[i] == '(') {  
            push(infix[i]); 
        } else if (infix[i] == ')') { 
            while (stack[top] != '(') {     
                postfix[j++] = pop();   
            } 
            pop(); 
        } else { 
            while (prior(stack[top]) >= prior(infix[i])) { 
                postfix[j++] = pop(); 
            } 
            push(infix[i]); 
        } 
    }   
    while (stack[top] != '#') {    
        postfix[j++] = pop();    
    } 
    postfix[j] = '\0'; 
} 

int main() { 
    char infix[MAX], postfix[MAX]; 

    printf("Enter an infix expression:\n"); 
    scanf("%s", infix); 

    infixToPostfix(infix, postfix); 

    printf("\nPostfix expression is:\n%s\n", postfix); 

    return 0; 
}
