/*
 * dswifitest_arm7.cpp
 *
 *  Created on: 29/08/2008
 *      Author: Michael Lunnay
 */

#include "../../../include/wifi.h"

void VblankHandler() {
	static int lastbut = -1;

	uint16 but=0, x=0, y=0, xpx=0, ypx=0, z1=0, z2=0;

	but = REG_KEYXY;

	if (!( (but ^ lastbut) & (1<<6))) {

		touchPosition tempPos = touchReadXY();

		if ( tempPos.x == 0 || tempPos.y == 0 ) {
			but |= (1 <<6);
			lastbut = but;
		} else {
			x = tempPos.x;
			y = tempPos.y;
			xpx = tempPos.px;
			ypx = tempPos.py;
			z1 = tempPos.z1;
			z2 = tempPos.z2;
		}

	} else {
		lastbut = but;
		but |= (1 <<6);
	}

	IPC->touchX			= x;
	IPC->touchY			= y;
	IPC->touchXpx		= xpx;
	IPC->touchYpx		= ypx;
	IPC->touchZ1		= z1;
	IPC->touchZ2		= z2;
	IPC->buttons		= but;

	Wifi_Update();
}

int main( int argc, char ** argv ) {
	irqInit();

	irqSet( IRQ_VBLANK, VblankHandler );
	irqEnable( IRQ_VBLANK );

	dl_init_wifi();		//set up everything wifi related

	while( true ) {
		swiWaitForVBlank();
	}
}
