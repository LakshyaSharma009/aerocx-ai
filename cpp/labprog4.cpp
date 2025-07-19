#include<stdio.h>
#include<stdlib.h>
struct node{
    int info;
    struct node *left;
    struct node *right;
};
typedef struct node *NODE;
NODE insert_front(int ,NODE);
NODE delete_data(int,NODE);
void display(NODE);

int main(){
    int item,ch;
    NODE head=NULL;
    while(1){
        printf("1:enter front\t2:delete data\t3:display\n");
        scanf("%d",&ch);
        switch(ch){
            case 1:printf("enter the element to enter\n");
                    scanf("%d",&item);
                    head=insert_front(item,head);
                    break;
        
            case 2:printf("enter the element to delete\n");
                    scanf("%d",&item);
                    head=delete_data(item,head);
            break;
            case 3:display(head);break;
            
            default:
                printf("enter valid choice\n");        

    }
}
}
NODE insert_front(int x, NODE head) {
     NODE temp = (NODE)malloc(sizeof(struct node)); 
     temp->info = x; 
     temp->left = NULL; 
     temp->right = head; 
     if (head != NULL) { 
        head->left = temp; } 
    return temp; }

NODE delete_data(int data, NODE head) {
    if (head == NULL) {
        printf("List is empty\n");
        return NULL;
    }

    NODE temp = head;

    // Search for the node with the given data
    while (temp->info != data) {
        temp = temp->right;
    }

    // If the element is not found
    if (temp == NULL) {
        printf("Element not found\n");
        return head;
    }

    printf("Found element: %d\n", temp->info);

    // Update pointers to remove the node
    if (temp->left == NULL) { // Node to be deleted is the head
        head = temp->right;
        if (head != NULL) {
            head->left = NULL;
        }
    } else {
        // If the node to be deleted is not the head node
        temp->left->right = temp->right;
    }

    if (temp->right != NULL) {
        temp->right->left = temp->left;
    }

    free(temp); // Free memory for the deleted node
    printf("Element %d deleted\n", data);
    return head;
}


void display(NODE head){
    if(head==NULL) printf("empty ll");
    NODE temp=head;

      do{  printf("%d->",temp->info);
        temp=temp->right;}
    while(temp!=NULL);
     printf("NULL\n");
}
