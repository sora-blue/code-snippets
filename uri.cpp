//next: hash duplicated files : completed
//next: make "hash-and-unique" a responsible part in the program
/*
Read image-uri from clipboard and convert it to .png images
through "certutil" provided under windows OS.

Recipe code style. Totally at a mess and can only applied
in windows system.

*/
#include <bits/stdc++.h>
#include <set>
#include <thread>
#include <windows.h>
HGLOBAL hGlobal;
PCHAR pCopied, pGlobal;
std::string savepath = "D:\\EnglishRoot\\image-collect\\";
std::string prefix = "image";
std::string suffix;
bool clear = false;
bool urilisten = false;
int getAvaIndex() {
	int index = 0;
	std::string filepath = savepath + prefix + std::to_string(index) + "." + suffix;
	WIN32_FIND_DATAA file;
	HANDLE han = FindFirstFile(filepath.c_str(), &file);
	while(han != (HANDLE)-1) {
		filepath = savepath + prefix + std::to_string(++index) + "." + suffix;
		han = FindFirstFile(filepath.c_str(), &file);
	}
	return index;
}
std::string getFromCb() {
	//get the handle
	OpenClipboard(GetDesktopWindow());
	hGlobal = GetClipboardData(CF_TEXT);
	if(!hGlobal) {
		throw std::runtime_error("Failed to read clipboard.");
		return "ERROR";
	}
	//allocate memory for the char array
	//lock global clipboard while reading
	//actually c-programming
	//PCHAR stands for pointer of char
	pCopied = new char[GlobalSize(hGlobal) + 10];
	pGlobal = (PCHAR)GlobalLock(hGlobal);
	strcpy(pCopied, pGlobal);
	GlobalUnlock(hGlobal);
	CloseClipboard();
	std::string data(pCopied);
	delete [] pCopied;
	return data;
}
std::tuple<bool, std::string, int> checkImageUri(const std::string& data) {
	if(data.substr(0,11) != "data:image/")
		return std::make_tuple(false,"ERROR-not-a-image-data-url", 0);
	int index = 11;
	while(data[index++] != ';'){}
	if(data.substr(index, 7) != "base64,")
		return std::make_tuple(false,"ERROR-not-base64", 0);
	return std::make_tuple(true, data.substr(11, index-12), index+7);
}
inline std::string& truncImageUri(std::string& data, int pos) {
	data.erase(0,pos);
	return data;
}
void clearTheSame() {
	/*
	Some images identify in content but not in size or sth
	This simple func can do nothing helpful to this currently.

	Also, it doesn't guarantee a stable order when deleting:)
	That is, it may delete files with higher or lower index.
	*/
	int  counter = 0;
	std::string tmpfile = "~tmp2.txt";
	std::string sub_suffix = std::string(" >> ") + tmpfile ;
	std::string sub_prefix = "certutil -hashfile " ;

	std::ifstream fin;
	WIN32_FIND_DATAA file;
	HANDLE han = FindFirstFile(std::string(savepath + "*.*").c_str(), &file);
	std::set<std::string> data; // wrong: it should have been defined in the outer space
	do {
		if(strcmp(file.cFileName, ".") == 0|| strcmp(file.cFileName, "..") == 0)
			continue;
		//1. make up a legal command
		std::string com_hash = sub_prefix + '"' +  savepath + file.cFileName  + '"' + sub_suffix ;
		std::string tmp;

		//2. execute it and save the result to <tmpfile>
		//3. read sha1 from <tmpfile>
		system(com_hash.c_str());
		fin.open(tmpfile);
		getline(fin, tmp);
		getline(fin, tmp);
		try {
hash_check:
			for(auto ite = tmp.begin() ; ite != tmp.end(); ++ite)
				if(!isalpha(*ite) && !isdigit(*ite)) throw std::runtime_error("sth-wrong-happened-with-hashfile-command\ntry-clear-tmpfiles");
		} catch(std::runtime_error&) {
			system(std::string(std::string("del ") + tmpfile).c_str());
			return;
		}
		std::cout << tmp << std::endl;
		fin.close();
		//4. check it with set
		auto ite = data.find(tmp);
		if(ite != data.end()) {
			std::string com_del = std::string("del ") + '"' +  savepath + file.cFileName  + '"';
			++counter;
			std::cout << com_del << std::endl;
			system(com_del.c_str());
		}
		data.insert(tmp);
		//5. del <tmpfile>
		system(std::string(std::string("del ") + tmpfile).c_str());
	} while(FindNextFile(han, &file));

	std::cout << "------------------------------- \n";
	std::cout << "It has tried to delete " << counter << " duplicated file(s) .\n";
	std::cout << "------------------------------- \n";
}
void generateCom() {
	std::string data = getFromCb();
	std::string tmpfilename = "~tmp.txt";
	std::vector<std::string> com {
		savepath.substr(0,2),
		std::string("cd ") + savepath,
		std::string("Certutil -decode ") + "\"" + savepath +  tmpfilename + "\" "
		//,std::string("attrib +h +s ") +  "\"" + savepath +  tmpfilename + "\" "
		//not just hide file, but actually make it untouchable
		,std::string("del ")+ "\"" + savepath +  tmpfilename + "\" "
	};
	auto afc = checkImageUri(data);
	std::ofstream fout(savepath + tmpfilename);
	int index = -1;
	if(!std::get<0>(afc)) {
		throw std::runtime_error("Invalid image-data-uri");
	}
	suffix = std::get<1>(afc);
	index = getAvaIndex();
	data = truncImageUri(data, std::get<2>(afc));
	fout << data;
	fout.close();
	com[2] = com[2] + "\"" + savepath + prefix + std::to_string(index) + "." + suffix + "\" ";
	for(long long unsigned int i = 0 ; i != com.size() ; ++i) {
		std::cout << com[i] << std::endl;
		system(com[i].c_str());
	}
	if(clear)
		clearTheSame();

	if(!urilisten) {
		std::cout << "have a see?(y/n)";
		char ch;

		//auto close after 1.2 seconds
		std::thread th([]() {
			if(!urilisten) { // it will automatically start ???
				Sleep(2000);
				exit(0);
			}

		});
		th.detach();
		/*
			join() : main thread needs to wait
			detach() : main thread and sub thread run simultaneously
		*/
		std::cin >> ch;
		if(ch == 'Y' || ch == 'y') {
			system(std::string(std::string("explorer ") + savepath).c_str());
		}
	}




}
int main(int args, char** argsv) { //throws IOException
	//data:image/png;base64,

	if(args > 1) {
		std::string settings[] = {"-c", "-l"};
		if(strlen(argsv[1]) == strlen(settings[0].c_str()) && strcmp(argsv[1], settings[0].c_str()) == 0) //clear
			clear = true;
		else if(strlen(argsv[1]) == strlen(settings[1].c_str()) && strcmp(argsv[1], settings[1].c_str()) == 0) //urilisten
			urilisten = true;
	}
	std::string previous_data;
	int uri_counter = 0;
	if(urilisten)
		std::cout << "listen mode is on... Watching you....your clipboard now" << std::endl;
	do {
		try {
			if(previous_data != getFromCb()) {

				try {
					generateCom();//real main func :)
					++uri_counter;
				} catch(std::runtime_error& err) {

					std::cerr << err.what();
					Sleep(3000);
				}

				previous_data = getFromCb();

				if(urilisten)
					std::cout << "It has tried to parse " <<  uri_counter << " image(s)." << std::endl;
				std::cout << std::endl;
			}
			if(urilisten)
				Sleep(500);

		} catch(std::exception& err) {
			std::cerr << err.what();
			Sleep(3000);
		}
	} while(urilisten);

	return 0;
}
//some codes are from:https://blog.csdn.net/ZhuMingYou3699/article/details/57455749
