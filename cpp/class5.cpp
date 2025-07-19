#include<iostream>
#include<string>
using namespace std;
class Teacher{
    private:
    float salary;
    public:
    Teacher(){
        dept="computer science";
    }
    string name;
    string dept;
    string sub;
    double setsal(float s){
        salary =s;
        return salary;
    }
    };
    int main(){
        Teacher t1;
        
        t1.name="lakshya";
        int newsal=t1.setsal(10000);
       
        cout<<t1.dept;

    }