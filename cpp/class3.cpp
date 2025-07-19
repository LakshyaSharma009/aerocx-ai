#include<iostream>
using namespace std;
class Employee
{public:
    int id;
    string name;
    float salary;
    
     
    void insert(int i,string n,float j){
        id=i;
        name=n;
        salary =j;
    }
    void display(){
        cout<<id<<" "<<name<<" "<<salary<<endl;
    }

};
int main(){
    Employee e1,e2,e3;
     
    e1.insert(1,"laksh",5000000);
e2.insert(2,"aksh",6851.646);
e3.insert(004,"alpha",6841353.66);
e1.display();
e2.display();
e3.display();
    return 0;
}