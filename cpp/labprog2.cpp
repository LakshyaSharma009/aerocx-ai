#include<stdio.h>
#define size 5
int main(){
    int insert(int *,int []);
    int qdelete(int *,int *,int []);
    int display(int ,int ,int []);
    int rear=-1,front=0,q[size],ch;
    while(1){
        printf("1:push 2:pop 3:display\n");
        scanf("%d",&ch);
        switch (ch){
            case 1:insert(&rear,q);break;
            case 2:qdelete(&front,&rear,q);break;
            case 3:display(front,rear,q);break;
            default:
                printf("enter valid choice");
        }}
        return 0;}
        int insert(int *rear,int q[]){
            int item;
            if(*rear==size-1) printf("stack is full");
            else
                {
                    printf("enter the element:");
                    scanf("%d",&item);
                    *rear=*rear+1;
                    q[*rear]=item;

                }
                return 0;
        }
        int qdelete(int *front,int *rear,int q[]){
            if(*front>*rear) printf("the queue is empty");
            else{
                    *front=*front+1;

            }
            return 0;
        }
        int display(int front,int rear,int q[]){
            int i;
            if(front>rear){
                printf("empty stack");

            }
            else{
                printf("the status of queue\n");
                for(i=front;i<=rear;i++){
                    printf("s[%d]=%d\t",i,q[i]);
                }
            }
            return 0;
        }

       
    