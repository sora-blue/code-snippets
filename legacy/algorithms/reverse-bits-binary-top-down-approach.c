#include<stdio.h>
int main()
{
    unsigned char r1, r2, r3, r4;
    __asm__("movb $0x9c, %0\n\t" 	// test number   = 0x9c = 0b10011100
            ""                   	// target number =        0b00111001 = 0x39
            ""
            ""                   	// Round 1
            "movb %0, %1\n\t"
            "movb %0, %2\n\t"
            "andb $0x0f, %1\n\t" 	// (0b10011100 & 0b00001111) = 0b00001100 = 0x0c
            "andb $0xf0, %2\n\t" 	// (0b10011100 & 0b11110000) = 0b10010000 = 0x90
            "shl $4, %1\n\t"    	// %1 = 0xc0
            "shr $4, %2\n\t"    	// %2 = 0x09
            "orb %2, %1\n\t"    	// result = %1 = 0xc9
            ""
            ""                  	// Round 2
            "movb %1, %0\n\t"
            "movb %1, %2\n\t"
            "andb $0x33, %0\n\t" 	// (0b11001001 & 0b00110011) = 0b00000001 = 0x01
            "andb $0xcc, %2\n\t" 	// (0b11001001 & 0b11001100) = 0b11001000 = 0xc8
            "shl $2, %0\n\t"    	// $0 = 0x04
            "shr $2, %2\n\t"    	// $2 = 0x32
            "orb %0, %2\n\t"    	// result = %2 = 0x36
            ""
            ""                  	// Round 3
            "movb %2, %0\n\t"
            "movb %2, %3\n\t"
            "andb $0x55, %0\n\t" 	// (0b00110110 & 0b01010101) = 0b00010100 = 0x14
            "andb $0xaa, %3\n\t" 	// (0b00110110 & 0b10101010) = 0b00100010 = 0x22
            "shl $1, %0\n\t"    	// $0 = 0x28
            "shr $1, %3\n\t"    	// $3 = 0x11
            "orb %0, %3\n\t"    	// result = %3 = 0x39
            ""
            "movb %3, %0\n\t" 	    // final result = 0x39
    :"+a"(r1), "+b"(r2), "+c"(r3), "+d"(r4));
    printf("r1(%%0): %x, r2(%%1): %x, r3(%%2): %x, r4(%%3): %x", r1, r2, r3, r4);
    return 0;
}
