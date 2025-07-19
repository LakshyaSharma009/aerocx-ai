#include<iostream>
using namespace std;
class Student
{public:
    int id;
    string name;
    
     
    Student(int i,string n){
        id=i;
        name=n;
    }
    ~Student(){
        cout<<"hello";
    }
    void display(){
        cout<<id<<" "<<name<<endl;
    }

};
int main(){
    Student s1=Student(10,"laksh");
     Student s2=Student(65,"aksh");
    
s1.display();
s2.display();
    return 0;
}