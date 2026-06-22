//
// Created by HP on 2021/9/19.
//

#ifndef AVG_JSON_AVG_JSON_H
#define AVG_JSON_AVG_JSON_H

/*
	Toy avg json generator

    20210919 by zzz: turn to std::shared_ptr<> instead of references as some strange errors occurred
    20210920 by zzz: implement some funcs for reading the file but not tested
    20210921 by zzz: complete getter-setter
    20211002 by zzz: complete read mode

    TO-DO List:
    1. prevent parse one node twice or more
    2. try to be thread-safe
    3. using template to support both std::wstring and std::string instead of ugly typedef AVG_STR_TYPE
    4. clean up code
    5. cmake & test & documentation
    6. JNI & front-end
*/

#pragma once

#include <cstddef>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <iomanip>
#include "json.hpp"

namespace avg {

#define AVG_LOG std::clog << "Warning: "

    typedef std::size_t AVG_INDEX_TYPE;
    typedef std::string AVG_STR_TYPE;
    typedef nlohmann::json AVG_JSON_TYPE;

    static const AVG_STR_TYPE NULL_STR;

    static const AVG_STR_TYPE AVG_JSONKEY_DATE = "date";
    static const AVG_STR_TYPE AVG_JSONKEY_NAME = "name";
    static const AVG_STR_TYPE AVG_JSONKEY_TYPE = "type";
    static const AVG_STR_TYPE AVG_JSONKEY_INDEX = "index";
    static const AVG_STR_TYPE AVG_JSONKEY_CONTENT = "content";
    static const AVG_STR_TYPE AVG_JSONKEY_OPTIONS = "options";
    static const AVG_STR_TYPE AVG_JSONKEY_LOCATION = "location";
    static const AVG_STR_TYPE AVG_JSONKEY_OTHERINFO = "otherInfo";
    static const AVG_STR_TYPE AVG_JSONKEY_TOP_AVGNAME = "avgName";
    static const AVG_STR_TYPE AVG_JSONKEY_TOP_AVGNODES  = "avgNodes";

    static const AVG_STR_TYPE AVG_JSONKEY_OPTION_CONTENT = "optionContent";
    static const AVG_STR_TYPE AVG_JSONKEY_OPTION_RESULT = "optionResult";

    static const AVG_STR_TYPE AVG_EVENT_DEFAULT_OPTION_NAME = "defaultOption";

    enum class avgNodeType {
        AVG_DIFF = 0,
        AVG_EVENT = 1,
        AVG_END = 2,
        AVG_OTHER = 3
    };

    class avgNode {
    protected:
        AVG_STR_TYPE  _content, _name, _otherInfo;
        std::size_t _index;
        avgNodeType _nodeType;
        AVG_JSON_TYPE json;
        struct option {
            std::string optionName, optionContent;
            std::size_t optionResult{}; // namely, 'next'
            std::size_t next() const{return optionResult;}
        };

    protected:
        avgNode(avgNodeType nodeType, std::size_t index, AVG_STR_TYPE content, AVG_STR_TYPE name = NULL_STR,
                AVG_STR_TYPE otherInfo = NULL_STR)
                : _nodeType(nodeType), _index(index), _content(content), _name(name), _otherInfo(otherInfo) {
            json[AVG_JSONKEY_NAME] = name;
            json[AVG_JSONKEY_INDEX] = index;
            json[AVG_JSONKEY_CONTENT] = content;
            json[AVG_JSONKEY_OTHERINFO] = otherInfo;
            json[AVG_JSONKEY_TYPE] = nodeType;
        }

    public:
        static avgNode* parseAvgNodeFromJson(const AVG_JSON_TYPE& json){
            //not managed by std::shared_ptr
            std::string name = json[AVG_JSONKEY_NAME] ;
            std::size_t index = json[AVG_JSONKEY_INDEX] ;
            std::string content = json[AVG_JSONKEY_CONTENT] ;
            std::string otherInfo = json[AVG_JSONKEY_OTHERINFO] ;
            auto nodeType = static_cast<avgNodeType>(json[AVG_JSONKEY_TYPE]);
            auto* node =  new avgNode(nodeType, index, content, name, otherInfo);
            node->json = json;
            return node;
        }

        AVG_JSON_TYPE dumpJson() {return json;}

        AVG_STR_TYPE dumpStr() {return json.dump();}
        bool isDiff(){return _nodeType == avgNodeType::AVG_DIFF;}
        bool isEvent(){return _nodeType == avgNodeType::AVG_EVENT;}
        bool isEnd(){return _nodeType == avgNodeType::AVG_END;}
        bool isOther(){return _nodeType == avgNodeType::AVG_OTHER;}
        //annoying getter-setter
        std::size_t getIndex(){return _index;}
        std::string getContent(){return _content;}
        std::string getName(){return _name;}
        std::string getOtherInfo(){return _otherInfo;}

        void setIndex(std::size_t index){
            _index = index;
            json[AVG_JSONKEY_INDEX] = _index;
        }
        void setContent(const std::string &content){
            _content = content;
            json[AVG_JSONKEY_CONTENT] = content;
        }
        void setName(const std::string &name){
            _name = name;
            json[AVG_JSONKEY_NAME] = name;
        }
        void setOtherInfo(const std::string &otherInfo){
            _otherInfo = otherInfo;
            json[AVG_JSONKEY_OTHERINFO] = otherInfo;
        }

        virtual std::vector<option> options(){
            return {};
        }
    };

    class avgDiff : public avgNode {
    protected:
        AVG_STR_TYPE _date, _location;
    public:
        avgDiff(std::size_t index, AVG_STR_TYPE date, AVG_STR_TYPE content, AVG_STR_TYPE location = NULL_STR,
                AVG_STR_TYPE name = NULL_STR, AVG_STR_TYPE otherInfo = NULL_STR)
                : avgNode(avgNodeType::AVG_DIFF, index, content, name, otherInfo), _date(date), _location(location) {
            json[AVG_JSONKEY_DATE] = date;
            json[AVG_JSONKEY_LOCATION] = location;
        }
        explicit avgDiff(const avgNode& node, AVG_STR_TYPE date, AVG_STR_TYPE location = NULL_STR): avgNode(node), _date(date), _location(location){
        }
        //annoying getter-setter
        std::string getDate(){return _date;}
        std::string getLocation(){return _location;}

        void setDate(const std::string &date){
            _date = date;
            json[AVG_JSONKEY_DATE] = date;
        }
        void setLocation(const std::string &location){
            _location = location;
            json[AVG_JSONKEY_LOCATION] = location;
        }

        static avgDiff* parseAvgDiffFromJson(const AVG_JSON_TYPE& json){
            std::shared_ptr<avgNode> node(parseAvgNodeFromJson(json));
            std::string date = json[AVG_JSONKEY_DATE];
            std::string location = json[AVG_JSONKEY_LOCATION];
            auto *diff = new avgDiff(*node, date, location);
            return diff;
        }

        avgDiff &addOption(AVG_STR_TYPE optionName, AVG_STR_TYPE optionContent, std::size_t optionResult) {
            if (json[AVG_JSONKEY_OPTIONS].contains(optionName)) {
                AVG_LOG << "duplicated option _name: " << optionName << "\n";
            }
            json[AVG_JSONKEY_OPTIONS][optionName][AVG_JSONKEY_OPTION_CONTENT] = optionContent;
            //AVG_STR_TYPE is set under consideration that i may use wstring or string
            // later, as avg games are mostly from Japan and charset is a big problem
            // to_string breaks the rule here
            // as it's nothing but a prototype, i'll fix it later once it works well
            json[AVG_JSONKEY_OPTIONS][optionName][AVG_JSONKEY_OPTION_RESULT] = optionResult;
            return *this;
        }

        std::vector<option> options() override{
            //low efficiency
            std::vector<option> options;
            for(const auto& item: json[AVG_JSONKEY_OPTIONS].items()){
                option o;
                o.optionName = item.key();
                o.optionContent = item.value()[AVG_JSONKEY_OPTION_CONTENT];
                o.optionResult = item.value()[AVG_JSONKEY_OPTION_RESULT];
                options.push_back(o);
            }
            return options;
        }

    };

    class avgEvent : public avgNode {
    protected:
        AVG_STR_TYPE _date, _location;
    public:
        avgEvent(std::size_t index, AVG_STR_TYPE date, AVG_STR_TYPE content, AVG_STR_TYPE location = NULL_STR,
                 AVG_STR_TYPE name = NULL_STR, AVG_STR_TYPE otherInfo = NULL_STR)
                : avgNode(avgNodeType::AVG_EVENT, index, content, name, otherInfo), _date(date), _location(location) {
            json[AVG_JSONKEY_DATE] = date;
            json[AVG_JSONKEY_LOCATION] = location;
            json[AVG_JSONKEY_OPTIONS][AVG_EVENT_DEFAULT_OPTION_NAME][AVG_JSONKEY_OPTION_RESULT] = 0u;
        }
        explicit avgEvent(const avgNode& node, AVG_STR_TYPE date, AVG_STR_TYPE location = NULL_STR): avgNode(node), _date(date), _location(location){}

        //annoying getter-setter
        std::string date(){return _date;}
        std::string location(){return _location;}

        avgEvent& setNext(std::size_t next_index) {
            if (json.is_object())
                json[AVG_JSONKEY_OPTIONS][AVG_EVENT_DEFAULT_OPTION_NAME][AVG_JSONKEY_OPTION_RESULT] = next_index;
            return *this;
        }
        static avgEvent* parseAvgEventFromJson(const AVG_JSON_TYPE& json){
            std::shared_ptr<avgNode> node(parseAvgNodeFromJson(json));
            std::string date = json[AVG_JSONKEY_DATE];
            std::string location = json[AVG_JSONKEY_LOCATION];
            auto *eve = new avgEvent(*node, date, location);
            return eve;
        }
        std::vector<option> options() override{
            option defaultO;
            defaultO.optionName = AVG_EVENT_DEFAULT_OPTION_NAME;
            defaultO.optionContent = "";
            defaultO.optionResult = json[AVG_JSONKEY_OPTIONS][AVG_EVENT_DEFAULT_OPTION_NAME][AVG_JSONKEY_OPTION_RESULT];
            return {defaultO};
        }
    };

    class avgEnd : public avgNode {
    public:
        static avgEnd* parseAvgEndFromJson(const AVG_JSON_TYPE& json){
            std::shared_ptr<avgNode> node(parseAvgNodeFromJson(json));
            auto *end = new avgEnd(*node);
            return end;
        }
        avgEnd(std::size_t index, AVG_STR_TYPE name, AVG_STR_TYPE content)
                : avgNode(avgNodeType::AVG_END, index, content, name) {

        }
        explicit avgEnd(const avgNode& node): avgNode(node){}
        std::vector<option> options() override{
            return {};
        }
    };

    //there should be a _base ...
    class avgNodeManager {
    private:
        std::vector<std::shared_ptr<avgNode>> avgQ;
        std::string mName, mFile;
        AVG_JSON_TYPE json;
        bool mode; // 0 w / 1 r
    private:
        void parseToAvgQ(const AVG_JSON_TYPE& qjson){
            avgQ.resize(qjson.size() + 10);
            for(auto& node: qjson){
                assert(node.is_object());
                // parse two times per time
                // it's a waste of time but easy to write
                avgNode *cur = avgNode::parseAvgNodeFromJson(node);
                if(cur->isDiff()){
                    avgQ.at(cur->getIndex()) = std::shared_ptr<avgDiff>(avgDiff::parseAvgDiffFromJson(node));
                }else if(cur->isEvent()){
                    avgQ.at(cur->getIndex()) = std::shared_ptr<avgEvent>(avgEvent::parseAvgEventFromJson(node));
                }else if(cur->isEnd()){
                    avgQ.at(cur->getIndex()) = std::shared_ptr<avgEnd>(avgEnd::parseAvgEndFromJson(node));
                }else{
                    throw std::runtime_error("parseToAvgQ: unknown type!");
                }
            }
        }
    public:
        explicit avgNodeManager(const std::string& mFile = "", const std::string& mode = "w") : mFile(mFile) {
            this->mode = (mode == "w");
            if(!this->mode){
                std::ifstream fin(mFile);
                if(!fin)
                    throw std::runtime_error("avgNodeManager: failed to open file " + mFile);
                try{
                    fin >> json;
                }catch (std::exception&){
                    std::cout << "fail to read\n";
                }

                fin.close();


                this->mName = json[AVG_JSONKEY_TOP_AVGNAME];
                parseToAvgQ(json[AVG_JSONKEY_TOP_AVGNODES]);
            }
        }


        void setName(const std::string &mName) {this->mName = mName;}
        std::string getName(){return this->mName;}

        //default constructors
        avgDiff &newDiff(AVG_STR_TYPE date, AVG_STR_TYPE content, AVG_STR_TYPE location = NULL_STR,
                         AVG_STR_TYPE name = NULL_STR, AVG_STR_TYPE otherInfo = NULL_STR) {
            //avg_str_type not applied
            avgQ.push_back(std::make_shared<avgDiff>(avgQ.size(), date, content, location, name, otherInfo));
            //not thread safe
            return *(avgDiff *)avgQ.back().get();
        }

        avgEvent &newEvent(AVG_STR_TYPE date, AVG_STR_TYPE content, AVG_STR_TYPE location = NULL_STR,
                           AVG_STR_TYPE name = NULL_STR, AVG_STR_TYPE otherInfo = NULL_STR) {
            //avg_str_type not applied
            avgQ.push_back(std::make_shared<avgEvent>(avgQ.size(), date, content, location, name, otherInfo));
            //not thread safe
            return *(avgEvent *)avgQ.back().get();
        }

        avgEnd &newEnd(AVG_STR_TYPE name, AVG_STR_TYPE content) {
            //avg_str_type not applied
            avgQ.push_back(std::make_shared<avgEnd>(avgQ.size(), name, content));
            //not thread safe
            return *(avgEnd *)avgQ.back().get();
        }

        avgNode * operator[](std::size_t index){
            //no check
            return this->avgQ[index].get();
        }
        avgNode * at(std::size_t index){
            if(index >= avgQ.size())
                throw std::runtime_error("at: out of range with getIndex" + std::to_string(index));
            return this->operator[](index);
        }

        AVG_JSON_TYPE dump_to_json() {
            AVG_JSON_TYPE return_json;
            return_json[AVG_JSONKEY_TOP_AVGNAME] = this->mName;
            for(std::size_t i = 0 ; i != avgQ.size() ; ++i){
                return_json[AVG_JSONKEY_TOP_AVGNODES][std::to_string(i)] = avgQ[i]->dumpJson();
            }
            return return_json;
        }

        std::string dump_to_str() {
            return dump_to_json().dump();
        }

        void dump_to_file() {
            if(!mode)
            {
                throw std::runtime_error ("dump_to_file: avgNodeManager is not in write mode and attempted to write.");
            }
            std::ofstream out_file(mFile);
            out_file << std::setw(4) << dump_to_json();
            out_file.close();
        }

        std::size_t size() {
            return avgQ.size();
        }
    };
}


#endif //AVG_JSON_AVG_JSON_H
