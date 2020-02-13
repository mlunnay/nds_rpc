/*
 * jsonrpc.h
 *
 *  Created on: 20/08/2008
 *      Author: Michael Lunnay
 *
 *  Taken from Mikael Klasson's devlight
 */

#ifndef JSONRPC_H_
#define JSONRPC_H_

#if defined(ARM7) || defined(ARM9)

#define BOOST_SP_DISABLE_THREADS

#endif

#include "wifi.h"
#include "value.h"
#include "tcpipconnection.h"
#include "except.h"
#include "methodcall.h"
#include "requester.h"
#include "response.h"

#endif // JSONRPC_H_
