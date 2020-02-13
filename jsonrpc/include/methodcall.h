/*
 * methodcall.h
 *
 *  Created on: 19/08/2008
 *      Author: Michael Lunnay
 */

#ifndef METHODCALL_H_
#define METHODCALL_H_

#include <string>

#include "value.h"

namespace jsonrpc {

	class MethodCall {
	public:
		MethodCall() : mName(), mParams(Array()), mId(++NextMethodId) {}

		MethodCall(const std::string& name) : mName(name), mParams(Array()), mId(++NextMethodId) {}

		// ~MethodCall() {} implicit destructor

		std::string getName() const { return mName; }

		void setName(const std::string& name) { mName = name; }

		int getId() const { return mId; }

		// return the json string that represents this method call
		// throws a RuntimeAssertionException if mName is empty
		std::string jsonString(const bool notification = false) const;

		// return true if parameters are given by name
		bool namedParams() const;

		// return true if parameters are given by position
		bool positionalParams() const;

		// clear the parameter list
		void clear();

		// return the number of parameters
		int size() const;

		// add a parameter to the parameter list
		// throws a RuntimeAssertionException if the parameter type is a non empty Object
		MethodCall& addParam(const Value& val);

		// adds a named parameter to the parameter list
		// throws a RuntimeAssertionException if the parameter type is a non empty Array
		MethodCall& addParam(const std::string& name, const Value& val);

		// clears the parameter list and sets its first value
		MethodCall& setParam(const Value& val);

		// clears the parameter list and sets its first named value
		MethodCall& setParam(const std::string& name, const Value& val);

		// returns the parameter at index
		// returns an empty Value if the parameter list is an Object
		Value getParam(const int index);

		// returns the parameter for the given key
		// returns an empty Value if the parameter list is an array or the key does not exist
		Value getParam(const std::string& name);

	private:
		std::string mName;
		Value mParams;
		int mId;
		static int NextMethodId;
	};

}  // namespace jsonrpc

#endif /* METHODCALL_H_ */
