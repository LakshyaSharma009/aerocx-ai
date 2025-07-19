#include<iostream>
#include<string>
using namespace std;
class Teacher{
    private:
    float salary;
    public:
    Teacher(string name,string dept,string sub,float salary){
        this->name =name;
        this->dept=dept;
        this->sub=sub;
        this->salary=salary;
    }
    string name;
    string dept;
    string sub;
    void getinfo(){
        cout<<"name is: "<<name<<endl;
        cout<<"salary is:"<<salary<<endl;
    }
    };
    int main(){
        Teacher t1("ananta","cs","math",123123);
        t1.getinfo();
        
      
    }