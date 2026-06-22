#include "avgJson.h"
using namespace avg;
using std::string;
//py-style print
auto print = [](const string &str){
    std::cout << str << std::endl;
};
void write_test()
{
    //create a sentakusiManager
    avgNodeManager avm0("../cppp.json", "w");
    avm0.setName("C++ prime plus");
    //create a sentakusi
    auto& avm0_n0 = avm0.newDiff("June 1st", "helol dworl debug:0x12345678 exception found", "classroom")
            .addOption("A", "run away", avm0.size() + 1)
            .addOption("B", "stay", avm0.size() + 2);
    // report : avm0.size() is evaluated before newDiff is executed.
    //create an event
    auto& avm0_n1 = avm0.newEvent("June 1st", "right choice", "classroom");
    auto& avm0_n2 = avm0.newEvent("June 1st", "compile error", "classroom");
    avm0_n1.setNext(avm0.size());
    avm0_n2.setNext(avm0.size());

    //create an end
    avm0.newEnd("Python Good End", "You gave up learning C++ and turned to python."); //, ...(optional other info)
    //output json file
    avm0.dump_to_file();
    std::string avm0_dumped = avm0.dump_to_str();
    std::cout << avm0_dumped;
    //not responsible for behaviors of anyone that uses it.
}
void dfs(avgNode *cur, avgNodeManager &avm, unsigned ground = 0){
    for(unsigned i = 0 ; i != ground ; i++)
            putchar('\t');
    if(cur->isEnd()){
        //if end, return
        print(cur->getContent());
        return;
    }
    //nnecessary info and spaces
    print(cur->getContent());
    for(auto stk : cur->options()){
        //sentakusi info
        print(stk.optionContent);
        printf("->");
        //sentakusi leads to
        dfs(avm[stk.next()], avm, ground + 1);
    }
}
void read_test()
{
    //read json
    avgNodeManager avm0("../cppp.json", "r");
    print("Name: " + avm0.getName());
    print("-------------------------------");
    //head node is at index 0 by default
    avgNode *head = avm0[0];
    dfs(head, avm0);
}
int main()
{
    write_test();
    read_test();
    return 0;
}
