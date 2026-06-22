// todo: upload to server
#define TT_WIN 1 
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <iostream>
#ifdef TT_WIN
#include <windows.h>
#endif
static int op[26];
static std::string fileName;
static std::string tmpf;
static FILE* pTmpFile;
static const char *configFile = "config.txt";
static const char *tempFile = "~.tmp";
static char pname[110];
#ifdef TT_WIN
static HWND fw;
#endif
static void del_tmp_file()
{
	if(!pTmpFile) return;
	fclose(pTmpFile);
	std::string com = "del " + tmpf;
	system(com.c_str());
}
static void wait_and_exit() { 
	del_tmp_file();
	#ifdef TT_WIN
	ShowWindow(fw, 1);
	#endif
	sleep(5);
	exit(0);
}
static void print_wait_and_exit() {
	static char desp[][110] = {
		"                                                                                                    ",
		"-d\t\tIf file exists, open it with notepad; else, create an empty txt file and open it with notepad.",
		"-f\t\tForce to create a new file even if a file with the same name exists.",
		"-r\t\tForce delete file (wait for implementation)",
		"-l\t\tList all files existing (w.f.i)",
		"Default path stores at: ./config.txt",
		"* Must starts with C:\\ or D:\\, etc.",
		"* Limit length: 1000 bytes"
	};
	sprintf((char *)desp, "Usage: %s [-d] [-f] [-r] [-l] [filename]", pname);
	int len = sizeof(desp) / sizeof(char[110]);
	for(int i = 0 ; i < len ; i++)
		printf("%s\n", desp[i]);
	wait_and_exit();
}
std::string get_new_name(const std::string &name)
{
	FILE *file = fopen(name.c_str(), "r");
	std::string newName;
	int i;
	for(i = 2 ; !file ; i++)
	{
		newName = name + " " + std::to_string(i);
		file = fopen(newName.c_str(), "r");
	}
	fclose(file);
	return newName;
	
}
std::string get_line(FILE *file)
{
	int ch = fgetc(file);
	std::string buf;
	while(ch != EOF && ch != '\n') 
	{
		buf += ch;
		ch = fgetc(file);
	}
	return buf;
}
void set_name(const char *name)
{
	int i, j;
	int len = strlen(name);
	for(i = len - 1; i >= 0 && name[i] != '.' ; i--)
	for(j = len - 1; j >= 0 && name[j] != '\\' && name[j] != '/'; j--)
	if(j < 0) j = 0;
	if(i < 0 || i < j) i = len;
	if(i <= j + 1)	return;
	
	memset(pname, 0, sizeof(pname));
	strncpy(pname, name + j + 1, i - j - 1);
}
int main(int argc, char **argv) {
	#ifdef TT_WIN
	fw = GetForegroundWindow();
	ShowWindow(fw, 0);
	#endif
	set_name(argv[0]);
	// analyse args
	if(argc < 2 || !strcmp(argv[1], "-?") || !strcmp(argv[1], "--help")) {
		print_wait_and_exit();
	}
	bool isOptionSet = false;
	for(int i = 1 ; i < argc ; i++) {
		if(argv[i][0] == '-') {
			int tmp = argv[i][1] - 'a';
			if(tmp > 25 || tmp < 0)
			{
				print_wait_and_exit();
				break; 
			}
			isOptionSet = true;
			op[tmp] = 1;
		}else{
			fileName = argv[i];
			break;
		}
	}
	// check legality
	if(!fileName.size() && !op['l' - 'a'])
	{
		printf("There's no filename.\n");
		wait_and_exit();
	}
	op['d' - 'a'] |= !isOptionSet;
	// read config file
	FILE *config = fopen(configFile, "r");
	if(config)
	{
		char buf[1024] = {0};
		int rc = 0;
		fread(buf, 1000, 1, config);
		rc = strlen(buf); 
		std::cerr << buf << std::endl;
		
		if(op['l' - 'a'])
		{
			std::string tmp = "explorer.exe ";
			tmp += buf;
			system(tmp.c_str());
			exit(0);
		}
		
		if(buf[rc-1] != '\\')
			buf[rc] = '\\';
		fileName = buf + fileName; 
		std::cerr << fileName << std::endl;
	}
	sleep(1);
	
	// check open status
	tmpf = fileName + tempFile;
	pTmpFile = fopen(tmpf.c_str(), "r");
	if(pTmpFile)
	{
		printf("File has been opened by us.\n");
		
		fclose(pTmpFile);
		pTmpFile = 0;
		
		wait_and_exit();
	}
	pTmpFile = fopen(tmpf.c_str(), "w");
	if(!pTmpFile)
	{
		printf("Tmp file failed to create.\n");
	}
	// check self del
	std::string self = argv[0];
	if(fileName == self || fileName == self + ".cpp" || fileName == self + ".exe")
	{
		printf("Not taking risk of wiping the program.\n");
		wait_and_exit();
	}
	//check suffix
	int len = fileName.size(), i;
	for(i = 0 ; i < len ; i++)
	{
		if(fileName[i] == '.')
		{
			break;
		}
	}
	if(i == len)
	{
		fileName += ".txt";
	}
	// 'f' option
	if(op['f' - 'a'])
	{
		FILE *newFile = fopen(fileName.c_str(), "w");
		if(!newFile)
		{
			printf("Failed to create file.\n");
			wait_and_exit();
		}
		fclose(newFile);
		std::string tmp = "notepad " + fileName;
		system(tmp.c_str());
		del_tmp_file();
		return 0;
	}
	// 'd' option
	if(op['d' - 'a'])
	{
		FILE *file = fopen(fileName.c_str(), "r");
		if(!file)
		{
			file = fopen(fileName.c_str(), "w");
			if(!file)
			{
				printf("Failed to create file.\n");
				wait_and_exit();
			}
		}
		fclose(file);
		std::string tmp = "notepad " + fileName;
		system(tmp.c_str());
		del_tmp_file();
		return 0;
	}
	del_tmp_file();
	return 0;
}
