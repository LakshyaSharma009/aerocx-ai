#include<iostream>
using namespace std;
class Student
{public:
    int id;
    string name;
    
     
    void insert(int i,string n){
        id=i;
        name=n;
    }
    void display(){
        cout<<id<<" "<<name<<endl;
    }

};
int main(){
    Student s1,s2;
     
    s1.insert(1,"laksh");
s2.insert(2,"aksh");
s1.display();
s2.display();
    return 0;
}