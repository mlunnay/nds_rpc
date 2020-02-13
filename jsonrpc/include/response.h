/*
 * response.h
 *
 *  Created on: 19/08/2008
 *      Author: Michael Lunnay
 */

#ifndef RESPONSE_H_
#define RESPONSE_H_

#include "value.h"

namespace jsonrpc {

	class Response {
	public:
		Response() : mError(false), mValue() {}

		explicit Response(const bool error) : mError(error), mValue() {}

		explicit Response(const Value& val): mError(false), mValue(val) {}

		Response(const bool error, const Value& val)
		: mError(error), mValue(val) {}

		// return true if this response is an error
		// if this is true then the result will be an Object
		// containing the keys: code, message, and optionally data
		bool isError() const { return mError; }

		// get the result value
		const Value& getResult() const { return mValue; }

		// set the result with a non error value
		void setResult(const Value& val);

		// set the response as an error with just an error code and a message
		void setError(const int code, const std::string& message);

		// set the response as an error with an error code, a message and extra data
		void setError(const int code, const std::string& message, const Value& val);

		void setError(const Value& val) {
			mError = true;
			mValue = val;
		}

	private:
		bool mError;
		Value mValue;
	};

}

#endif /* RESPONSE_H_ */
