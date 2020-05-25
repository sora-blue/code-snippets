#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <iostream>
// robot map_inside[x][y]=1
// person map_inside[x][y]=2
using std::cin;
using std::cout;
using std::endl;
char map[4][4],per='X',robot='Y',temp;
int map_inside[4][4],x,y,pper,rrot,bal;
int d[][2]= {
    {0,1},{0,-1},{1,0},{-1,0},
    {1,1},{1,-1},{-1,1},{-1,-1}
};
int check_empty     ();
int check_win       ();
bool check_rules    (int,int);
bool check_able     (int,int,int);
bool robot_random_chess   ();
bool robot_strategy_jugde (int);
bool robot_strategy_normal(bool);
void robot_strategy ();
void game_goingOn   ();
void print();
void reset();
void first();
int main() {
    std::srand(std::time(0));
    while(true)
    {
        first();
        game_goingOn();
        printf("\nWant another One?(Y/N)");
        cin>>temp;
        if(temp!='Y'&&temp!='y') break;
    }
    printf("\nWin:%d Lose:%d Balance:%d\n",pper,rrot,bal);
    system("pause");
    return 0;
}
int check_empty() {
#define map map_inside
    int ans = 0;
    for(int i=1; i<=3; ++i) {
        for(int j=1; j<=3; ++j) {
            if(map[i][j]==0)
                ++ans;
        }
    }
    return ans;
#undef map
}
int check_win() {
#define map map_inside
    for(int i=1; i<=2; ++i) {
        if(map[1][1]==i&&map[1][2]==i&&map[1][3]==i)
            return i;
        if(map[1][1]==i&&map[2][1]==i&&map[3][1]==i)
            return i;
        if(map[1][1]==i&&map[2][2]==i&&map[3][3]==i)
            return i;
        if(map[1][2]==i&&map[2][2]==i&&map[3][2]==i)
            return i;
        if(map[1][3]==i&&map[2][3]==i&&map[3][3]==i)
            return i;
        if(map[1][3]==i&&map[2][2]==i&&map[3][1]==i)
            return i;
        if(map[2][1]==i&&map[2][2]==i&&map[2][3]==i)
            return i;
        if(map[3][1]==i&&map[3][2]==i&&map[3][3]==i)
            return i;
    }
#undef map
    return 0;
}
inline bool check_rules(int x,int y) {
    if(x<1||x>3||y<1||y>3) return false;
    return true;
}
bool check_able(int hang,int lie,int node) {
    bool ok = true;
    for(int i=1; i<=3&&ok; ++i) {
        if(map_inside[hang][i]!=node&&map_inside[hang][i]!=0)
            ok = false;
    }
    if(ok) return true;
    for(int i=1; i<=3&&ok; ++i) {
        if(map_inside[i][lie]!=node&&map_inside[hang][i]!=0)
            ok = false;
    }
    return ok;
}
bool robot_strategy_jugde(int node) {
    for(int i=1; i<=3; ++i) {
        for(int j=1; j<=3; ++j) {
            if(map_inside[i][j]==node) {
                int t1=i,t2=j;
                for(int k=0; k<8; ++k) {
                    t1=i+d[k][0];
                    t2=j+d[k][1];
                    if(!check_rules(t1,t2)) continue;
                    if(map_inside[t1][t2]==node) {
                        t1+=d[k][0];
                        t2+=d[k][1];
                        if(!check_rules(t1,t2)) continue;
                        if(map_inside[t1][t2]) continue;
                        map[t1][t2]=robot;
                        map_inside[t1][t2]=1;
                        return true;
                    }
                }
                for(int k=0; k<8; ++k) {
                    t1=i+d[k][0]*2;
                    t2=j+d[k][1]*2;
                    if(!check_rules(t1,t2)) continue;
                    if(map_inside[t1][t2]==node) {
                        t1-=d[k][0];
                        t2-=d[k][1];
                        if(!check_rules(t1,t2)) continue;
                        if(map_inside[t1][t2]) continue;
                        map[t1][t2]=robot;
                        map_inside[t1][t2]=1;
                        return true;
                    }
                }
            }
        }
    }
    return false;
}
bool robot_strategy_normal(bool able) {
    for(int i=1; i<=3; ++i) {
        for(int j=1; j<=3; ++j) {
            if(map_inside[i][j]==0&&(!able||check_able(i,j,2))) {
                map[i][j]=robot;
                map_inside[i][j]=1;
                return true;
            }
        }
    }
    return false;
}
bool robot_random_chess(){
    for(int i=1;i<=9;++i){
        int x=std::rand()%3+1;
        int y=std::rand()%3+1;
        if(!check_rules(x,y)) continue;
        if(map_inside[x][y]) continue;
        map_inside[x][y]=1;
        map[x][y]=robot;
        return true;
    }
    return false;
}
void robot_strategy() {
    if(robot_strategy_jugde(1)||robot_strategy_jugde(2)) return;
    if(robot_random_chess()) return;
    if(robot_strategy_normal(true)) return;
    robot_strategy_normal(false);
}

void game_goingOn() {

    while(check_empty()>0&&check_win()==0) {
Robot_Hand:
        robot_strategy();
Show_Part1:
        system("cls");
        print();
Check_Part2:
        if(check_win()!=0||check_empty()==0) break;
Person_Hand:
        x=y=0;
        while(
            !check_rules(x,y)
            ||map_inside[x][y]
        ) {
                printf("input Chess's Position :x y \n"),
                cin>>x>>y;
                if(!check_rules(x,y)) printf("OutOfRange\n");
                if(map_inside[x][y]) printf("PositionOccupied\n");
                if(cin.fail()) return;
        }
        map_inside[x][y]=2;
        map[x][y]=per;
    }
    system("cls");
    print();
    if      (check_win()==1)
        printf("YOU LOSE!"),++rrot;
    else if (check_win()==2)
        printf("YOU WIN!"),++pper;
    else
        printf("NO ONE WINS"),++bal;
}
void print() {
    for(int i=1; i<=3; ++i) {
        for(int j=1; j<=3; ++j) {
            printf("%c\t",map[i][j]);
        }
        printf("\n");
    }
}
void reset() {
    for(int i=1; i<=3; ++i) {
        for(int j=1; j<=3; ++j) {
            map[i][j]='0';
        }
    }
    memset(map_inside,0,sizeof(map_inside));
}
void first() {
    reset();
    printf("Want first hand or not?(Y\\N)");
    cin>>temp;
    x=y=0;
    if(
        (temp=='Y'||temp=='y')
        &&!check_rules(x,y)
    ) {
            while(!check_rules(x,y)){
                printf("input Chess's Position :x y \n"),
                cin>>x>>y;
                if(!check_rules(x,y)) printf("OutOfRange\n");
                if(map_inside[x][y]) printf("PositionOccupied\n"),x=y=0;
                if(cin.fail()) return;
            }
    }
    map_inside[x][y]=2;
    map[x][y]=per;
    system("cls");
    print();
}

