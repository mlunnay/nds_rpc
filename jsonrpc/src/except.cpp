/*
 * except.cpp
 *
 *  Created on: 14/08/2008
 *      Author: Michael Lunnay
 */

#include "../include/except.h"

#include <sstream>

namespace jsonrpc {
	Exception::Exception(int ec, const std::string &s):
		mCode(ec),
		mDescription(s),
		mType(),
		mFile(),
		mLine(0),
		mFullDescription() {}

	Exception::Exception(int ec, const std::string &s, const char* type, const char* file, long line ):
		mCode(ec),
		mDescription(s),
		mType(type),
		mFile(file),
		mLine(line),
		mFullDescription() {}

	Exception::Exception(const Exception& rhs):
		mCode(rhs.mCode),
		mDescription(rhs.mDescription),
		mType(rhs.mType),
		mFile(rhs.mFile),
		mLine(rhs.mLine),
		mFullDescription() {}

	Exception& Exception::operator=(const Exception& rhs) {
		mCode = rhs.mCode;
		mDescription = rhs.mDescription;
		mType = rhs.mType;
		mFile = rhs.mFile;
		mLine = rhs.mLine;
		mFullDescription.clear();

		return *this;
	}

	const std::string& Exception::getFullDescription(void) const {
		if (mFullDescription.empty()) {

			std::stringstream desc;

			desc <<  "JSON-RPC EXCEPTION(" << mCode << ":" << mType << "): "
				<< mDescription;

			if( mLine > 0 )
			{
				desc << " at " << mFile << " (line " << mLine << ")";
			}

			mFullDescription = desc.str();
		}

		return mFullDescription;
	}
}

