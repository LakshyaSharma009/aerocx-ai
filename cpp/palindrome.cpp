#include<iostream>
using namespace std;
int main(){
    int n,first=0,second=1,next;
    cout<<"enter no of terms";
    cin>>n;
    for(int i=0;i<n;i++){
        cout<<first<<endl;
        next=first+second;
        first=second;
        second=next;

    }
}