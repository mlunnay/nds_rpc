/*
 * tcpipconnection.h
 *
 *  Created on: 25/08/2008
 *      Author: Michael Lunnay
 */

#ifndef TCPIPCONNECTION_H_
#define TCPIPCONNECTION_H_

#include <string>
#include <boost/function.hpp>
#ifdef _WIN32
	#include <winsock.h>
#endif
#if defined(ARM9)
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <netdb.h>
	#include "wifi.h"
#endif

namespace jsonrpc {

	// a class representing an outgoing TCP/IP Connection
	class TCPIPConnection {
	public:
		TCPIPConnection(const std::string& host, int port);

		~TCPIPConnection();

		void connect();

		void disconnect();

		// Convenience method for sending an entire string and receiving all of the reply
		// calls connect, write, read, disconnect and returns the result.
		std::string sendRecieve(const std::string& buff);

		// write data to this connection
		// len is the max length of buff to send, if this is 0 the whole string will be written.
		// callback is any callable object that takes two unsigned ints, and returns a bool
		// this is passed the bytes written so far, and the total length if known or 0.
		// if the callback returns false writing to the connection will cease.
		void write(const std::string& buff, const long len = 0,
				boost::function<bool (unsigned int, unsigned int)> callback = 0) const;

		// read data from this connection, returns a string containing the data
		// len is the max length to read, if this is 0 all possible data will be read
		// callback is any callable object that takes two unsigned ints, and returns a bool
		// this is passed the bytes read so far, and the total length if known or 0.
		// if the callback returns false reading from the connection will cease.
		std::string read(const long len = 0,
				boost::function<bool (unsigned int, unsigned int)> callback = 0) const;

		// returns the last error code from the underlying socket library
		int getError();

		// returns the string representation of the last error from the underlying socket library
		std::string getErrorString();

		// return the port that this connection is connected to.
		int getPort() const { return mPort; }

		// return the host name of this system
		std::string getHostName() const { return mHostName; }

		// return the host name of the system we are connected to.
		std::string getPeerName() const { return mPeerName; }

		// return the ip address of the system we are connected to.
		std::string getPeerAddress() const { return mPeerAddress; }

	private:
		TCPIPConnection() {}
//		void init(const std::string& host, int port);

		int mSocketfd;
		std::string mHostName;
		int mPort;
		std::string mPeerName;
		std::string mPeerAddress;
		struct sockaddr_in mTheirAddr;
	};

}

#endif /* TCPIPCONNECTION_H_ */
