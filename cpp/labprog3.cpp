#include<stdio.h>
#include<stdlib.h>
struct node{
    int info;
    struct node *ptr;
};
typedef struct node *NODE;
NODE insert_front(int ,NODE);
NODE delete_front(NODE);
void adisplay(NODE);
NODE insert_middle(int,int,NODE);
int main(){
    int item,ch,pos;
    NODE head=NULL;
    while(1){
        printf("1:enter front\t2:delete front\t3:display\t4:insert in pos\n");
        scanf("%d",&ch);
        switch(ch){
            case 1:printf("enter the element to enter\n");
                    scanf("%d",&item);
                    head=insert_front(item,head);
                    break;
        
            case 2:head=delete_front(head);
            break;
            case 3:adisplay(head);break;
            case 4:printf("enter the element to enter\n");
                    scanf("%d",&item);
                    printf("enter the position to enter:\n");
                    scanf("%d",&pos);
                    head=insert_middle(item,pos,head);
                    break;
            default:
                printf("enter valid choice\n");        

    }
}
}
NODE insert_front(int x,NODE head){
    
    NODE temp=(NODE)malloc(sizeof(struct node));
    temp->info=x;
    temp->ptr=head;
    return temp;
}
NODE delete_front(NODE head){
    if(head==NULL) printf("empty loln\n");
    else if(head->ptr==NULL){
        free(head);
        return NULL;

    }
    else{
        head=head->ptr;
        return head;
    }
}
void adisplay(NODE head){
    if(head==NULL) printf("empty ll");
    NODE temp=head;

    while(temp!=NULL){
        printf("%d->",temp->info);
        temp=temp->ptr;
    } printf("\n");
}
NODE insert_middle(int x,int pos,NODE head){
    NODE temp=(NODE)malloc(sizeof(struct node));
    temp->info=x;
    temp->ptr=NULL;
    NODE p=head;
    for(int i=1;i<pos-1;i++){
        p=p->ptr;
    }
    temp->ptr=p->ptr;
    p->ptr=temp;
    return head;
}