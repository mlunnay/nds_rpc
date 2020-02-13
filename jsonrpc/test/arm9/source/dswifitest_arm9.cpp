/*
 * dswifitest.cpp
 *
 *  Created on: 29/08/2008
 *      Author: Michael Lunnay
 */

#include <nds.h>
#include "../../../include/jsonrpc.h"

using namespace jsonrpc;

class ConnectCallback {
public:
	ConnectCallback(): mCount(0), mSubCount(0) {}

	bool operator()(int x) {
		if(mCount++ & 0x1f) {
			swiWaitForVBlank();
			return true;
		}

		char mod = mSubCount % 4;
		if(mSubCount++ != 0)
			iprintf("\x1b[1D");

		switch(mod) {
		case 0:
			iprintf("-");
			break;
		case 1:
			iprintf("\\");
			break;
		case 2:
			iprintf("|");
			break;
		case 3:
			iprintf("/");
			break;
		}

		swiWaitForVBlank();
		return true;
	}

private:
	int mCount;
	int mSubCount;
};

int main(void) {
	lcdMainOnBottom();
	powerON( POWER_ALL_2D );

	irqInit();

	irqSet( IRQ_VBLANK, 0 );
	irqEnable( IRQ_VBLANK );

	consoleDemoInit();
	BG_PALETTE[0] = BG_PALETTE_SUB[0] = RGB15( 31, 31, 31 );
	BG_PALETTE_SUB[255] = RGB15( 0, 0, 31 );

	iprintf("Starting rpc test\n");
	iprintf("initializing wifi\n");

	if( !Wifi_CheckInit() ) init_wifi();
	iprintf("autoconnecting wifi");
	Wifi_AccessPoint ap = {
			"101", 3, {0x00,0x09,0x0b,0x70,0x4d,0x86}, {0,0,0,0,0,0},
			0, 0, 0, 0, 0, 6, {0,0,0,0,0,0,0,0},
			{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
	};
//	if( !autoconnect_wifi(ConnectCallback()) ) {
	if( !connect_wifi(&ap, 0, 0, 0, ConnectCallback()) ) {
		iprintf("\nUnable to connect to network via WIFI\n");
		return 1;
	}

	unsigned long ip = Wifi_GetIP();
	iprintf("\nconnected with ip: %d.%d.%d.%d\n",
			(int)(ip & 0xff),
			(int)(ip >> 8 & 0xff),
			(int)(ip >> 16 & 0xff),
			(int)(ip >> 24 & 0xff));

//	iprintf("testing jsonrpc to 192.168.1.3:50042\n");
//
//	TCPIPConnection conn("192.168.1.3", 50042);
	iprintf("testing jsonrpc to 172.16.28.122:50042\n");

	TCPIPConnection conn("172.16.28.122", 50042);
	Requester req(conn);

	MethodCall call("system.echo");
	call.addParam(String("test")).addParam(Number(42));
	call.addParam(Bool(true)).addParam(Null());

	try {
		Response ret = req.call(call);

		if(ret.isError()) {
			iprintf("req.call returned an error.\n");
			Object res = value_cast<Object>(ret.getResult());
			iprintf("code: %d\n", static_cast<int>(value_cast<Number>(res["code"]).getValue()));
			iprintf("message: %s\n", value_cast<String>(res["message"]).getValue().c_str());
		}
		else {
			iprintf("req.call returned a result:\n");
			iprintf("%s\n", ret.getResult().jsonString().c_str());
			Array arr = value_cast<Array>(ret.getResult());
			iprintf("Value 1: %s\n", value_cast<String>(arr[0]).getValue().c_str());
			iprintf("Value 2: %d\n", static_cast<int>(value_cast<Number>(arr[1]).getValue()));
			iprintf("Value 3: %s\n", (value_cast<Bool>(arr[2]).getValue() == true) ? "true" : "false");
			iprintf("Value 4: %s\n", arr[3].isNull() ? "is Null" : "should be Null");
		}

	} catch(const Exception& e) {
		iprintf("Exception: %s\n", e.what());
	}

	Wifi_DisconnectAP();
	Wifi_DisableWifi();

	return 0;
}
