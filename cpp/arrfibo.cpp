#include<iostream>
using namespace std;
int main(){
   int arr[100];
   int n,i;
   cout<<"enter n:";
   cin>>n;
   arr[0]=0;
   arr[1]=1;

   for(i=2;i<n;i++){
    
    arr[i]=arr[i-1]+arr[i-2];
   }
   for(i=0;i<n;i++){
   cout<<arr[i];}
}
 

