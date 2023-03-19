#include <bits/stdc++.h>
using namespace std;
class Solution {
    vector<string> sentence2words(const string &sentence){
        vector<string> ans;
        string tmp;
        for(int i = 0 ; i < sentence.size() ; i++){
            if(isspace(sentence[i])){
                if(tmp.size() > 0){
                    ans.push_back(tmp);
                    tmp = "";
                }
                continue;
            }
            tmp += sentence[i];
        }
        if(tmp.size() > 0)
            ans.emplace_back(move(tmp));
        return ans;    
    }  
    string words2sentence(const vector<string> &words){
        string ans;
        for(int i = 0 ; i < words.size() ; i++){
            ans += words[i] + "\n";
        }
        return ans;
    }
public:
    string fullJustify(const string &sentence, int maxWidth) {
        auto words = sentence2words(sentence);
        vector<string> ans;
        vector<string> buf;
        int cnt = maxWidth;
        int i, j, k;
        for(i = 0 ; i < words.size() ; i++){
            int tmp;
            tmp = words[i].size() + !!buf.size();
            if(cnt >= tmp){
                cnt -= tmp;
                buf.push_back(words[i]);
            }else{
                string line;
                if(buf.size() == 1){
                    cnt = maxWidth - buf.back().size();
                    line += buf.back();
                    for(k = 0 ; k < cnt ; k++){
                        line += ' ';
                    }
                }else{
                    cnt += buf.size() - 1;
                    tmp = cnt % (buf.size() - 1);
                    cnt = cnt / (buf.size() - 1);
                
                    for(j = 0 ; j < buf.size() - 1; j++){
                        line += buf[j];
                        for(k = 0 ; k < cnt + !!tmp; k++){
                            line += ' ';
                        }
                        if(tmp > 0){
                            tmp--;
                        }
                    }
                    line += buf.back();
                }
                ans.push_back(line);
                buf.clear();
                cnt = maxWidth;
                i--;
            }
        }
        // last line
        string line;
        cnt = maxWidth;
        for(j = 0 ; j < buf.size() - 1; j++){
            line += buf[j] + ' ';
            cnt  -= buf[j].size() + 1;
        }
        line += buf.back();
        cnt -= buf.back().size();
        for(k = 0 ; k < cnt ; k++){
            line += ' ';
        }
        ans.push_back(line);
        return words2sentence(ans);
    }
};
int main(int argc, char **argv){
    int limit = 30;
    if(argc > 1){
        limit = stoi(argv[1]);
    }
    Solution so;
    string input;
    getline(cin, input);
    cout << so.fullJustify(input, limit);
    return 0;
}
