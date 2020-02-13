/*
 * parse.cpp
 *
 *  Created on: 20/08/2008
 *      Author: Michael Lunnay
 */

#include <string>

#include "../include/parse.h"
#include "../external/tinyjson/tinyjson.hpp"

namespace jsonrpc {

	// recursive function to transform json variant into Values
	Value constructValue(const json::grammar<char>::variant& var) {
		if(var->empty()) {
			return Value(Null());
		}
		else if(var->type() == typeid(bool)) {
			// variant is a Bool
			return Value(Bool(boost::any_cast< bool >(*var)));
		}
		else if(var->type() == typeid(int)) {
			// variant is a Number
			return Value(Number(boost::any_cast< int >(*var)));
		}
		else if(var->type() == typeid(double)) {
			// variant is a Number
			return Value(Number(boost::any_cast< double >(*var)));
		}
		else if(var->type() == typeid(std::string)) {
			// variant is a String
			return Value(String(boost::any_cast< std::string >(*var)));
		}
		else if(var->type() == typeid(json::grammar<char>::array)) {
			// variant is an Array
			json::grammar<char>::array const & a = boost::any_cast< json::grammar<char>::array >(*var);
			Array arr;
			for(json::grammar<char>::array::const_iterator it = a.begin(); it != a.end(); ++it) {
				arr.push_back(constructValue(*it));
			}

			return Value(arr);
		}
		else if(var->type() == typeid(json::grammar<char>::object))
		{
		  // variant is an object => use recursion
			json::grammar<char>::object const & o = boost::any_cast< json::grammar<char>::object >(*var);
			Object obj;
			for(json::grammar<char>::object::const_iterator it = o.begin(); it != o.end(); ++it) {
				std::string strName = (*it).first;
				obj[strName] = constructValue((*it).second);
			}

			return Value(obj);
		}

		return Value(Null());
	}

}
