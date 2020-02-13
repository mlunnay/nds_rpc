/*
 * except.h
 *
 *  Created on: 14/08/2008
 *      Author: Michael Lunnay
 *
 *	custom exception heirarcy for json-rpc
 */

#ifndef JSONRPC_EXCEPT_H_
#define JSONRPC_EXCEPT_H_

#include <exception>
#include <string>

#define JSONRPC_EXCEPT(num, desc) throw jsonrpc::ExceptionFactory::create( \
	jsonrpc::ExceptionCodeType<num>(), desc, __FILE__, __LINE__ );

#define JSONRPC_ASSERT(a, b) if( !(a) ) JSONRPC_EXCEPT(jsonrpc::Exception::ECRTAssertionFailed, (b))

namespace jsonrpc {

class Exception : public std::exception {
public:

	// Exception codes that use the same domain as the json-rpc error codes
	// this will allow for json-rpc error objects to be represented as exceptions
	enum ExceptionCodes {
		// json-rpc error codes
		ECParseError = -32700,
		ECInvalidRequest = -32600,
		ECMethodNotFound = -32601,
		ECInvalidParams = -32602,
		ECInternalError = -32603,
		// application json-rpc defined server error codes
		ECApplicationError = -32000,
		ECAssertionFailed = -32001,
		ECNotImplemented = -32002,
		// library error codes
		ECRTAssertionFailed = -3000,
		ECSystemError = -3001,
		ECBadCast = -3002,
		ECIOError = -3003,
		ECTransportError = -3004,
		ECActionCanceled = -3005	// thrown when action is canceled via a callback etc.
	};

	Exception(int ec, const std::string &s);

	Exception(int ec, const std::string &s, const char* type, const char* file, long line );

	Exception(const Exception& rhs);

	Exception& operator=(const Exception& rhs);

	virtual ~Exception() throw() {}

	virtual const std::string getDescription() const { return mDescription; }

	virtual const std::string& getFullDescription(void) const;

	virtual int getExceptionCode() const { return mCode; }

	virtual const std::string getType() const { return mType; }

	virtual const std::string getFile() const { return mFile; }

	virtual int getLine() const { return mLine; }

	// override std::exception::what
	virtual const char *what() const throw() { return getFullDescription().c_str(); }

private:

	int mCode;
	std::string mDescription;
	std::string mType;
	std::string mFile;
	int mLine;

	mutable std::string mFullDescription;
};

	// this is adapted from Ogre

	/** Template struct which creates a distinct type for each exception code.
	@note
	This is useful because it allows us to create an overloaded method
	for returning different exception types by value without ambiguity.
	From 'Modern C++ Design' (Alexandrescu 2001).
	*/
	template <int num>
	struct ExceptionCodeType
	{
		enum { number = num };
	};

	// Specialised exceptions allowing each to be caught specifically
	// backwards-compatible since exception codes still used

	class ParseErrorException : public Exception	{
	public:
		ParseErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "ParseErrorException", file, line) {}
	};

	class InvalidRequestException : public Exception	{
	public:
		InvalidRequestException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "InvalidRequestException", file, line) {}
	};

	class MethodNotFoundException : public Exception	{
	public:
		MethodNotFoundException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "MethodNotFoundException", file, line) {}
	};

	class InvalidParametersException : public Exception	{
	public:
		InvalidParametersException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "InvalidParametersException", file, line) {}
	};

	class InternalErrorException : public Exception	{
	public:
		InternalErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "InternalErrorException", file, line) {}
	};

	class ApplicationErrorException : public Exception	{
	public:
		ApplicationErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "ApplicationErrorException", file, line) {}
	};

	class AssertionFailedException : public Exception	{
	public:
		AssertionFailedException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "AssertionFailedException", file, line) {}
	};

	class NotImplementedException : public Exception	{
	public:
		NotImplementedException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "NotImplementedException", file, line) {}
	};

	class RuntimeAssertionException : public Exception	{
	public:
		RuntimeAssertionException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "RuntimeAssertionException", file, line) {}
	};

	class SystemErrorException : public Exception	{
	public:
		SystemErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "SystemErrorException", file, line) {}
	};

	class BadCastException : public Exception	{
	public:
		BadCastException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "BadCastException", file, line) {}
	};

	class IOErrorException : public Exception	{
	public:
		IOErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "IOErrorException", file, line) {}
	};

	class TransportErrorException : public Exception	{
	public:
		TransportErrorException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "TransportErrorException", file, line) {}
	};

	class ActionCanceledException : public Exception	{
	public:
		ActionCanceledException(int number, const std::string& description, const char* file, long line)
			: Exception(number, description, "ActionCanceledException", file, line) {}
	};

	/** Class implementing dispatch methods in order to construct by-value
		exceptions of a derived type based just on an exception code.
	@remarks
		This nicely handles construction of derived Exceptions by value (needed
		for throwing) without suffering from ambiguity - each code is turned into
		a distinct type so that methods can be overloaded. This allows JSONRPC_EXCEPT
		to stay small in implementation (desirable since it is embedded) whilst
		still performing rich code-to-type mapping.
	*/
	class ExceptionFactory {
	private:
		/// Private constructor, no construction
		ExceptionFactory() {}
	public:
		static ParseErrorException create(
			ExceptionCodeType<Exception::ECParseError> code,
			const std::string& desc, const char* file, long line) {
			return ParseErrorException(code.number, desc, file, line);
		}
		static InvalidRequestException create(
			ExceptionCodeType<Exception::ECInvalidRequest> code,
			const std::string& desc, const char* file, long line) {
			return InvalidRequestException(code.number, desc, file, line);
		}
		static MethodNotFoundException create(
			ExceptionCodeType<Exception::ECMethodNotFound> code,
			const std::string& desc, const char* file, long line) {
			return MethodNotFoundException(code.number, desc, file, line);
		}
		static InvalidParametersException create(
			ExceptionCodeType<Exception::ECInvalidParams> code,
			const std::string& desc, const char* file, long line) {
			return InvalidParametersException(code.number, desc, file, line);
		}
		static InternalErrorException create(
			ExceptionCodeType<Exception::ECInternalError> code,
			const std::string& desc, const char* file, long line) {
			return InternalErrorException(code.number, desc, file, line);
		}
		static ApplicationErrorException create(
			ExceptionCodeType<Exception::ECApplicationError> code,
			const std::string& desc, const char* file, long line) {
			return ApplicationErrorException(code.number, desc, file, line);
		}
		static AssertionFailedException create(
			ExceptionCodeType<Exception::ECAssertionFailed> code,
			const std::string& desc, const char* file, long line) {
			return AssertionFailedException(code.number, desc, file, line);
		}
		static NotImplementedException create(
			ExceptionCodeType<Exception::ECNotImplemented> code,
			const std::string& desc, const char* file, long line) {
			return NotImplementedException(code.number, desc, file, line);
		}
		static RuntimeAssertionException create(
			ExceptionCodeType<Exception::ECRTAssertionFailed> code,
			const std::string& desc, const char* file, long line) {
			return RuntimeAssertionException(code.number, desc, file, line);
		}
		static SystemErrorException create(
			ExceptionCodeType<Exception::ECSystemError> code,
			const std::string& desc, const char* file, long line) {
			return SystemErrorException(code.number, desc, file, line);
		}
		static BadCastException create(
			ExceptionCodeType<Exception::ECBadCast> code,
			const std::string& desc, const char* file, long line) {
			return BadCastException(code.number, desc, file, line);
		}
		static IOErrorException create(
			ExceptionCodeType<Exception::ECIOError> code,
			const std::string& desc, const char* file, long line) {
			return IOErrorException(code.number, desc, file, line);
		}
		static TransportErrorException create(
			ExceptionCodeType<Exception::ECTransportError> code,
			const std::string& desc, const char* file, long line) {
			return TransportErrorException(code.number, desc, file, line);
		}
		static ActionCanceledException create(
			ExceptionCodeType<Exception::ECActionCanceled> code,
			const std::string& desc, const char* file, long line) {
			return ActionCanceledException(code.number, desc, file, line);
		}
	};
}

#endif /* JSONRPC_EXCEPT_H_ */
