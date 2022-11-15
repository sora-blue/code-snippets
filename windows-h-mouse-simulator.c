#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <windows.h>
//SetCursorPos(x, y);
//mouse_event(MOUSEEVENTF_LEFTDOWN|MOUSEEVENTF_LEFTUP,0,0,0,0);
//MessageBox(0,"1","2",0);
int main(){
	HWND fw = GetForegroundWindow();ShowWindow(fw, 0); 
	POINT p;
	Sleep(3000);
	GetCursorPos(&p);
	printf("%d %d\n", p.x, p.y);
	//return 0; 
	p.x = 468;
	p.y = 562;
	for(int i = 1 ; i < 32 ; i++){
		if(GetKeyState(27) < 0){
			//MessageBox(0,"1","2",0);
			break;
		}
		SetCursorPos(p.x, p.y);
		mouse_event(MOUSEEVENTF_LEFTDOWN|MOUSEEVENTF_LEFTUP,0,0,0,0);
		Sleep(100);
	}
	//MessageBox(0,"1","2",0);
	return 0;
}
