// todo: upload to server
// 标准化配置文件
// 在参数中自由选择vim或notepad，并将选择记录下来
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
static std::string tmpF;
static FILE* pTmpFile;
static const char *configFile = "./config.txt";
static const char *tempFile = "~.tmp";
static char pName[110];
static int DEBUGGING = 0;
static HWND fw;
static std::string git_prefix;
static void del_tmp_file()
{
    if(!pTmpFile) return;
    fclose(pTmpFile);
    std::string com = "del " + tmpF;
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
// exit hook
int clear0kb(char *oFilePath);
static void normal_exit(char *buf) {
	del_tmp_file();
    clear0kb(buf);
    
	std::string com1 = git_prefix + " add .";
	std::string com2 = git_prefix + " commit -m \"tt auto commit\"";
    system(com1.c_str());
    system(com2.c_str());
    
    if(DEBUGGING){
    	printf("Program's auto to exit. [debug mode]\n");
    	system("pause");
	}
	exit(0);
}
static void print_wait_and_exit() {
    static char description[][110] = {
            "                                                                                                    ",
            "-d\t\tIf file exists, open it with notepad; else, create an empty txt file and open it with notepad.",
            "-f\t\tForce to create a new file even if a file with the same name exists.",
            "-r\t\tForce delete file (wait for implementation)",
            "-l\t\tList all files existing (w.f.i)",
            "Default path stores at: ./config.txt",
            "* Must starts with C:\\ or D:\\, etc.",
            "* Limit length: 1000 bytes"
    };
    sprintf((char *)description, "Usage: %s [-d] [-f] [-r] [-l] [filename]", pName);
    int len = sizeof(description) / sizeof(char[110]);
    for(int i = 0 ; i < len ; i++)
        printf("%s\n", description[i]);
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
    for(i = len - 1; i >= 0 && name[i] != '.' ; i--){
    	for(j = len - 1; j >= 0 && name[j] != '\\' && name[j] != '/'; j--){
    		if(j < 0) j = 0;
            if(i < 0 || i < j) i = len;
            if(i <= j + 1)	return;
		}
	}
        

    memset(pName, 0, sizeof(pName));
    strncpy(pName, name + j + 1, i - j - 1);
}
int clear0kb(char *oFilePath)
{
    WIN32_FIND_DATA fileData;
    int tmpLen = strlen(oFilePath);
    if(!tmpLen){
    	return 1;
	}
    char filePath[3030];
    char tmpFilePath[3030];
    printf("%s\n", filePath);
    sprintf(filePath, "%s*.*", oFilePath);

    HANDLE file = FindFirstFile(filePath, &fileData);
    bool result = file;
    int cnt = 0;
    while (result)
    {
        memset(filePath, 0, sizeof(filePath));
        memset(tmpFilePath, 0, sizeof(tmpFilePath));
        size_t fileSize = (fileData.nFileSizeHigh * (MAXDWORD + 1)) + fileData.nFileSizeLow;
        if(fileSize){
            result = FindNextFile(file, &fileData);
            continue;
        }
        if(strlen(fileData.cFileName) && fileData.cFileName[0] == '.'){
            result = FindNextFile(file, &fileData);
            continue;
        }
        sprintf(tmpFilePath, "%s%s", fileData.cFileName, tempFile);
        HANDLE tmp = FindFirstFile(tmpFilePath, nullptr);

        if(tmp != INVALID_HANDLE_VALUE){
            result = FindNextFile(file, &fileData);
            continue;
        }

		int rs1;
		sprintf(tmpFilePath, "%s%s", oFilePath, fileData.cFileName);
		printf("%s\n", tmpFilePath);
        rs1 = DeleteFile(tmpFilePath);
        result = FindNextFile(file, &fileData);
		cnt += !!rs1;
    }
    printf("%d 0kb file(s) cleared.\n", cnt);
    FindClose(file);
#ifdef TT_WIN
    if(cnt){
        ShowWindow(fw, 1);
        sleep(2);
    }
#endif
	return 0;
}
int main(int argc, char **argv) {
    set_name(argv[0]);
    fw = GetForegroundWindow();
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
    DEBUGGING = op['b' - 'a'];
    // not debug mode
    if(!DEBUGGING){
     	ShowWindow(fw, 0);
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
    char buf[1024] = {0};
    if(config)
    {
        
        fread(buf, 1000, 1, config);
        int rc = strlen(buf);
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
            
         {
        	std::string com = "git -C ";
    		std::string bufs = buf;
    		int len = bufs.length();
			com += "\"";
			com += bufs.substr(0, len-1);	
			com += "\" ";
			git_prefix = com;
		}
        fileName = buf + fileName;
        std::cerr << fileName << std::endl;
        
        // git support 
        // cmd.exe's closing gives ~.tmp file to notepad (lol)
        std::string gitRepo = std::string(buf) + ".gitignore";
        FILE *gitFile = fopen(gitRepo.c_str(), "r");
        if(!gitFile){
        	gitFile = fopen(gitRepo.c_str(), "w");
        	if(!gitFile){
        		printf("Warning: failed to create git repo");
        		wait_and_exit();
			}else{
				const char *gitInfo = ".tmp\n";
				fwrite(gitInfo, strlen(gitInfo), 1, gitFile);
				fclose(gitFile);
				std::string com = git_prefix + " init";
				std::cerr << com << std::endl;
				system(com.c_str());
			}
		} 
    }
    
    // sleep(1);

    // check open status
    tmpF = fileName + tempFile;
    pTmpFile = fopen(tmpF.c_str(), "r");
    if(pTmpFile)
    {
        printf("File has been opened by us.\n");

        fclose(pTmpFile);
        pTmpFile = 0;

        wait_and_exit();
    }
    pTmpFile = fopen(tmpF.c_str(), "w");
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
        std::string tmp = "vim " + fileName;
        system(tmp.c_str());
        normal_exit(buf);
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
        std::string program;
        if(op['v' - 'a'])
            program = "vim.lnk";
        else if(op['s' - 'a'])
            program = "notepad3";
        else
            program = "notepad";
        std::string tmp = program + " " + fileName;
        system(tmp.c_str());
        normal_exit(buf);
        return 0;
    }
    normal_exit(buf);
    return 0;
}
