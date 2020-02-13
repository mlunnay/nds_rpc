/*
 * tcpipconnection.cpp
 *
 *  Created on: 25/08/2008
 *      Author: Michael Lunnay
 */

#include <vector>
#include <errno.h>

#include "../include/tcpipconnection.h"
#include "../include/except.h"
#include <iostream>
#include <nds.h>
namespace jsonrpc {

	const int MAXBUFFSIZE = 4096;

	TCPIPConnection::TCPIPConnection(const std::string& host, int port)
	: mSocketfd(-1) {
#ifdef _WIN32
		WSADATA wsaData;
		WSAStartup(MAKEWORD(1, 1), &wsaData);
#endif

		struct hostent *he;

		if( !inet_aton( host.c_str(), &mTheirAddr.sin_addr ) ) {
			if ((he=gethostbyname(host.c_str())) == NULL) {  // get the host info
				mSocketfd = -1;
				JSONRPC_EXCEPT(-3004, std::string("network connection failed: ") + strerror(errno))
			}
			mTheirAddr.sin_addr = *((struct in_addr *)he->h_addr_list[0]);
			mPeerName = std::string(he->h_name);
			mPeerAddress = std::string(he->h_addr_list[0]);
		}


		mTheirAddr.sin_family = AF_INET;    // host byte order
		mTheirAddr.sin_port = htons(port);  // short, network byte order

		memset(mTheirAddr.sin_zero, '\0', sizeof mTheirAddr.sin_zero);

		char hostname[128];

		if(gethostname(hostname, sizeof(hostname)) == -1) {
			JSONRPC_EXCEPT(-3004, std::string("network connection failed: ") + strerror(errno))
		}

		mHostName = std::string(hostname);
		mPort = port;
	}

	TCPIPConnection::~TCPIPConnection() {
#ifdef _WIN32
		WSACleanup();
#endif
		closesocket(mSocketfd);
	}

	void TCPIPConnection::connect() {
		if(mSocketfd != -1)
			return;

		if ((mSocketfd = socket(PF_INET, SOCK_STREAM, 0)) == -1) {
			JSONRPC_EXCEPT(-3004, std::string("network connection failed: ") + strerror(errno))
		}

		iprintf("attempting to connect to remote host:\n");
		iprintf(" host ip: %d.%d.%d.%d\n",
			(int)(mTheirAddr.sin_addr.s_addr & 0xff),
			(int)(mTheirAddr.sin_addr.s_addr >> 8 & 0xff),
			(int)(mTheirAddr.sin_addr.s_addr >> 16 & 0xff),
			(int)(mTheirAddr.sin_addr.s_addr >> 24 & 0xff));
		iprintf(" host port: %d\n", (int)(ntohs(mTheirAddr.sin_port)));


		if (::connect(mSocketfd, (struct sockaddr *)&mTheirAddr,
											  sizeof mTheirAddr) == -1) {
			JSONRPC_EXCEPT(-3004, std::string("network connection failed: ") + strerror(errno))
		}
	}

	void TCPIPConnection::disconnect() {
#ifdef _WIN32
		closesocket(mSocketfd);
#elif NDS
		close(mSocketfd);
#endif
		mSocketfd = -1;
	}

	// Convenience method for sending an entire string and receiving all of the reply
	// calls connect, write, read, disconnect and returns the result.
	std::string TCPIPConnection::sendRecieve(const std::string& buff) {
		std::string ret;
		connect();
		try {
			write(buff);
			ret = read();
		} catch (const Exception& e) {
			disconnect();
			throw e;
		}
		disconnect();
		return ret;
	}

	// write data to this connection
	// len is the max length of buff to send, if this is 0 the whole string will be written.
	void TCPIPConnection::write(const std::string& buff, const long len,
			boost::function<bool (unsigned int, unsigned int)> callback) const {
		long tlen = 0;
		long total = 0;
		long sendlen = 0;

		if(len == 0)
			tlen = buff.size();
		else
			tlen = len;

		while(total < tlen) {
			int size = tlen - total;
			if(size > MAXBUFFSIZE)
				size = MAXBUFFSIZE;
			if((sendlen = send(mSocketfd, buff.substr(total, size).c_str(), size, 0)) == -1) {
				JSONRPC_EXCEPT(-3004, std::string("network send failed: ") + strerror(errno))
			}
			total += sendlen;

			if(callback) {
				if(!callback( total, tlen)) {
					JSONRPC_EXCEPT(-3005, std::string("write canceled by callback"))
				}
			}
		}
	}

	// read data from this connection, returns a string containing the data
	// len is the max length to read, if this is 0 all possible data will be read
	std::string TCPIPConnection::read(const long len,
			boost::function<bool (unsigned int, unsigned int)> callback) const {
		char buf[MAXBUFFSIZE + 1];
		int total = 0;
		int numbytes = MAXBUFFSIZE;
		std::string out;

		while(numbytes == MAXBUFFSIZE) {
			int recvlen = len - total;
			if(recvlen > MAXBUFFSIZE || recvlen <= 0)
				recvlen = MAXBUFFSIZE;

			if ((numbytes=recv(mSocketfd, buf, recvlen, 0)) == -1) {
				JSONRPC_EXCEPT(-3004, std::string("network recv failed: ") + strerror(errno))
			}
			out.append(buf, numbytes);
			total += numbytes;

			if(callback) {
				if(!callback( total, len)) {
					JSONRPC_EXCEPT(-3005, std::string("read canceled by callback"))
				}
			}
		}

		return out;
	}

	// returns the last error code from the underlying socket library
	int TCPIPConnection::getError() {
		return errno;
	}

	// returns the string representation of the last error from the underlying socket library
	std::string TCPIPConnection::getErrorString() {
		return strerror(errno);
	}

}
