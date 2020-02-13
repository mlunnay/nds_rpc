/*
 * parse.h
 *
 *  Created on: 20/08/2008
 *      Author: Michael Lunnay
 */

#ifndef PARSE_H_
#define PARSE_H_

#include <string>

#include "value.h"
#include "except.h"
#include "../external/tinyjson/tinyjson.hpp"

namespace jsonrpc {

	Value constructValue(const json::grammar<char>::variant& var);

	template <typename Iterator>
	Value parse(Iterator const & szBegin, Iterator const & szEnd) {
		json::grammar<char>::variant v = json::parse(szBegin, szEnd);

		if(v->type() != typeid(json::grammar<char>::object)) {
			// if the return type of json::parse is not an object there was a parse error
			JSONRPC_EXCEPT(Exception::ECParseError, "Error parsing json input")
		}

		return constructValue(v);
	}
}

#endif /* PARSE_H_ */
