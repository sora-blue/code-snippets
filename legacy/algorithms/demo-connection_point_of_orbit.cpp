#include <bits/stdc++.h>
using namespace std;
// simplified connection point detector
// implements: Elements of Programming (CHN edition), Alexander Stepanov, Page 26
template<typename value_type>
struct LinkedNode{
    typedef LinkedNode<value_type>* pointer_type;
    typedef LinkedNode<value_type>* const const_pointer_type;
    typedef function<bool(pointer_type)> unary_predicator_type;
    typedef function<pointer_type(pointer_type)> transformer_type;
    //
    friend std::ostream& operator <<(std::ostream &os, LinkedNode<value_type> node);
    //
    value_type val;
    pointer_type next;
    //
    LinkedNode(value_type val, pointer_type next) : val(val), next(next) {}
    explicit LinkedNode(value_type val) : LinkedNode(val, nullptr) {}
    LinkedNode() : LinkedNode(0) {}
    //
    static bool not_empty(pointer_type p){
        return p != nullptr;
    }
    static pointer_type advance(pointer_type p){
        if(!not_empty(p)) return p;
        return p->next;
    }
    //
    static LinkedNode *collision_point
    (const_pointer_type x, transformer_type f, unary_predicator_type p){
        if(!p(x)) return x;
        pointer_type slow = x;
        pointer_type fast = f(x);
        while(fast != slow){
            slow = f(slow);
            if(!p(fast)) return fast;
            fast = f(fast);
            if(!p(fast)) return fast;
            fast = f(fast);
        }
        return fast;
    }
    //
    static bool terminating
    (const_pointer_type x, transformer_type f, unary_predicator_type p){
        return !p(collision_point(x, f, p));
    }
    //
    static pointer_type convergent_point
    (pointer_type x0, pointer_type x1, transformer_type f){
        while(x0 != x1){
            x0 = f(x0);
            x1 = f(x1);
        }
        return x0;
    }
    //
    static pointer_type connection_point
    (const_pointer_type x, transformer_type f, unary_predicator_type p){
        pointer_type y = collision_point(x, f, p);
        if(!p(y)) return y;
        return convergent_point(x, f(y), f);
    }
    //
};
std::ostream& operator <<(std::ostream &os, LinkedNode<int> *node){
    if(!LinkedNode<int>::not_empty(node)){
        os << "<none>";
        return os;
    }
    os << "<" << node->val << ">";
    return os;
}
int main() {
    // build the orbit
    // * mem leak! just for test
    auto p1 = new LinkedNode<int>(0);
    LinkedNode<int> *pre = p1;
    for(int i = 0 ; i < 8 ; i++){
        pre = new LinkedNode<int>(i+1, pre);
    }
    p1->next = pre;
    auto p2 = new LinkedNode<int>(-1, pre);
    auto p3 = new LinkedNode<int>(-2, p2);
    //
    auto pn = LinkedNode<int>::connection_point(p3, LinkedNode<int>::advance, LinkedNode<int>::not_empty);
    auto pl = LinkedNode<int>::collision_point(p3, LinkedNode<int>::advance, LinkedNode<int>::not_empty);
    cout << "collision_point: " << pl << endl;
    cout << "connection_point: " << pn << endl;
    return 0;
}
