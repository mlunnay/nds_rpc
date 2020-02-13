/*
 * wifi.h
 *
 *  Created on: 20/08/2008
 *      Author: Michael Lunnay
 *
 *  Taken from Mikael Klasson's devlight
 */

#ifndef WIFI_H_
#define WIFI_H_

#include <nds.h>

#ifdef ARM9
#include <string>
#include <boost/function.hpp>
#include <dswifi9.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#endif

#ifdef ARM7
#include <dswifi7.h>
#endif

#ifdef ARM9

//sends text string (null terminated string) to <socket>
int send( int socket, const char * text );

//initialize wifi functionality. must be done after 2d init, as swiWaitForVblank() is called.
void init_wifi();

//autoconnect to the default AP
// callback is called every pass with the current status,
// if this returns false the function will stop attempting to connect.
//return bool: true on success.
bool autoconnect_wifi(boost::function<bool (int)> callback = 0);

// This function encapsulates Wifi_ConnectAP and Wifi_AssocStatus
// allowing an optional callback that is called with the current status
// if this returns false the function will stop attempting to connect.
// returns bool: true on success.
bool connect_wifi(Wifi_AccessPoint * apdata, int wepmode, int wepkeyid,
		unsigned char * wepkey,
		boost::function<bool (int)> callback = 0);

//initializes a socket <sock> to host ip/name <host>.
//return bool: true on success.
bool init_socket( int * sock, char * host, int port, bool blocking = true );

#endif

#ifdef ARM7

void dl_init_wifi();

#endif //ARM7

#endif // WIFI_H_
