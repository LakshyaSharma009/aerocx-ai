#include<stdio.h>
#define size 5
int main(){
    int push(int *,int []);
    int pop(int *,int []);
    int display(int ,int []);
    int top=-1,s[size],ch;
    while(1){
        printf("1:push 2:pop 3:display\n");
        scanf("%d",&ch);
        switch(ch){
            case 1:push(&top,s);break;
            case 2:pop(&top,s);break;
            case 3:display(top,s);break;
            default:
                printf("enter valid choice");
        }}
        return 0;}
        int push(int *top,int s[]){
            int item;
            if(*top==size-1) printf("stack is full");
            else
                {
                    printf("enter the element:");
                    scanf("%d",&item);
                    *top=*top+1;
                    s[*top]=item;

                }
                return 0;
        }
        int pop(int *top,int s[]){
            if(*top==-1) printf("the stack is empty");
            else{
                    *top=*top-1;

            }
            return 0;
        }
        int display(int top,int s[]){
            int i;
            if(top==-1){
                printf("empty stack");

            }
            else{
                printf("the status of stack\n");
                for(i=0;i<=top;i++){
                    printf("s[%d]=%d\t",i,s[i]);
                }
            }
            return 0;
        }

       
    