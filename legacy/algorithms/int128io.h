//C++ oriented. I/O support for __int128 of GCC.
#ifndef _INT128_IO
#define _INT128_IO

#ifndef _GLIBCXX_IOSTREAM
#define _GLIBCXX_IOSTREAM
#include <iostream>
#endif

#ifndef _INC_STDIO
#define _INC_STDIO
#include <cstdio>
#endif
namespace std {
	void _write(__int128 t) {
		if(t >= 10)
			_write(t / 10);
		putchar(t % 10 + '0');
	}
	__int128 _read() {
		__int128 _ = 0 , ___ = 1;
		char __ = getchar();
		while(__ < '0' || __ > '9') {
			if(__ == '-') ___ = -1;
			__ = getchar();
		}
		while(__ >= '0' && __ <= '9') {
			_ = _ * 10 + __ - '0';
			__ = getchar();
		}
		return _ * ___;
	}
	std::ostream& operator <<(std::ostream &os, const __int128 &t) {
		_write(t);
		return os;
	}
	std::istream& operator >>(std::istream &is, __int128 &t) {
		t = _read();
		return is;
	}
}
#endif
