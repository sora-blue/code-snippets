#include <windows.h>
#include <stdio.h>

/*
80% by ChatGPT 3.5
It's NOT an old-fashioned program made with love (lmao)
*/

int main(int argc, char *argv[]) {
	int interval = 7000; // Default interval is 7000ms
	bool paused = false;

	// Parse the interval from command line arguments (second)
	if (argc >= 2) {
		interval = atoi(argv[1]) * 1000;
	}

	printf("Waiting ...\n");
	// Wait for 5 seconds before starting
	Sleep(5000);
	printf("Executing ...\n");

	// Send the down arrow key every interval milliseconds
	while (true) {
		if (!paused) {
			// Press the down arrow key
			keybd_event(VK_DOWN, 0, 0, 0);

			// Wait for a short time
			Sleep(50);

			// Release the down arrow key
			keybd_event(VK_DOWN, 0, KEYEVENTF_KEYUP, 0);
		}

		int check_int = 100;
		// Check if the spacebar is pressed
		for(int cnt = 0; cnt < interval / check_int; cnt++) {
			if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) {
				paused = !paused;
				if (paused) {
					printf("Paused\n");
				} else {
					printf("Resumed\n");
				}
			}
			// Wait for a short time to avoid detecting multiple key presses
			// Also for pausing.
			Sleep(100);
		}

	}

	return 0;
}
