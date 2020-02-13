/*
 * value.h
 *
 *  Created on: 12/08/2008
 *      Author: Michael Lunnay
 *
 *	Json type objects
 */

#ifndef JSONRPC_VALUE_H_
#define JSONRPC_VALUE_H_

#if defined(ARM7) || defined(ARM9)

#define BOOST_SP_DISABLE_THREADS

#endif

#include <tr1/memory>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <typeinfo>
#include <boost/type_traits/remove_reference.hpp>

#include "except.h"

namespace jsonrpc {

	enum ValueType {
		VTNull = 0,
		VTBool,
		VTNumber,
		VTString,
		VTArray,
		VTObject
	};

	// forward class declarations needed by Value
	class Null;
	class Bool;
	class Number;
	class String;
	class Array;
	class Object;
	class ValueBase;

	// an abstraction of ValueBase providing factory style construction
	// and casting functionality.
	// this is a variant type for JSON types.
	class Value {
	public:
		typedef std::tr1::shared_ptr<Value> ptr;
		typedef std::tr1::shared_ptr<ValueBase> value_type;

		Value();

		// copy constructor
		Value(const Value& val);

		// create a Value from a shared_ptr<ValueBase>
		Value(const value_type& val);

		// These constructors create a shared pointer to a copy of the value passed
		Value(const Null& val);

		Value(const Bool& val);

		Value(const Number& val);

		Value(const String& val);

		Value(const Array& val);

		Value(const Object& val);

		// possibly add construction from bool, int, double, and strings

		Value& operator=(const Value& rhs);
		Value& operator=(const value_type& rhs);

		friend bool operator==(const Value&, const Value&);
		friend bool operator<(const Value&, const Value&);

		value_type getValue() { return mValue; }
		const value_type getValue() const { return mValue; }

		ValueType getType() const;

		bool isType(ValueType val) const;

		std::string jsonString() const;

		std::string typeString() const;

		// type determination functions
		bool isNull() const;

		bool isBool() const;

		bool isNumber() const;

		bool isString() const;

		bool isArray() const;

		bool isObject() const;

		// casting moved to functions due to advice from Effective C++
		// casting
		// the cast to values throw a AssertionFailedException if the ValueType does not match the type trying to be cast.
		// but the shared_ptr<T> just uses dynamic_pointer_cast<T> so the user needs to check if shared_ptr<T>.get() == 0 for wrong cast.
//		operator Null&();
//		operator const Null&() const;
//		operator std::tr1::shared_ptr<Null>();
//
//		operator Bool&();
//		operator const Bool&() const;
//		operator std::tr1::shared_ptr<Bool>();
//
//		operator Number&();
//		operator const Number&() const;
//		operator std::tr1::shared_ptr<Number>();
//
//		operator String&();
//		operator const String&() const;
//		operator std::tr1::shared_ptr<String>();
//
//		operator Array&();
//		operator const Array&() const;
//		operator std::tr1::shared_ptr<Array>();
//
//		operator Object&();
//		operator const Object&() const;
//		operator std::tr1::shared_ptr<Object>();

	private:
		template<typename ValueType>
		friend ValueType * value_cast(Value *);

		value_type mValue;
	};

	class ValueBase {
	public:
		typedef std::tr1::shared_ptr<ValueBase> ptr;

		ValueBase(ValueType t) : mType(t) {}
		virtual ~ValueBase() {}

		bool operator==(const ValueBase& other) const;
		bool operator!=(const ValueBase& other) const;
		bool operator<(const ValueBase& other) const;

		ValueType getType() const { return mType; }

		bool isType(ValueType t) const { return (t == mType); }

		// return a string representation of the JSON Value
		std::string jsonString() const {
			return doJsonString();
		}

		// return a string with the json parameter type
		std::string typeString() const {
			return doTypeString();
		}

	private:
		// compare two values of the derived type return -1 for less than other 0 for equal and 1 for greater than other
		virtual int compare(const ValueBase& other) const = 0;

		virtual std::string doJsonString() const = 0;

		virtual std::string doTypeString() const = 0;

		ValueType mType;
	};

	// Value comparisons here because they rely on the fully defined ValueBase
	inline bool operator==(const Value& x, const Value& y) {
		return *(x.mValue.get()) == *(y.mValue.get());
	}

	inline bool operator<(const Value& x, const Value& y) {
		return *(x.mValue.get()) < *(y.mValue.get());
	}

	inline bool operator!=(const Value& x, const Value& y) {
		return !(x == y);
	}

	inline bool operator>(const Value& x, const Value& y) {
		return y < x;
	}

	inline bool operator<=(const Value& x, const Value& y) {
		return !(y < x);
	}

	inline bool operator>=(const Value& x, const Value& y) {
		return !(x < y);
	}

	class Null : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<Null> ptr;

		Null() : ValueBase(VTNull) {}

		// Nulls have no real value so all nulls are equal
		bool operator==(const Null& other) const { return true; }
		bool operator!=(const Null& other) const { return false; }

	private:
		int compare(const ValueBase& other) const { return 0; }

		std::string doJsonString() const { return "null"; }

		virtual std::string doTypeString() const { return "nil"; }
	};

	class Bool : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<Bool> ptr;

		Bool() : ValueBase(VTBool), mValue(true) {}
		Bool(bool value) : ValueBase(VTBool), mValue(value) {}

		bool operator==(const Bool& other) const { return (mValue == other.mValue); }
		bool operator!=(const Bool& other) const { return (mValue != other.mValue); }

		bool getValue() const { return mValue; }
		void setValue(const bool value) { mValue = value; }

	private:
		int compare(const ValueBase& other) const;

		std::string doJsonString() const {
			if(mValue)
				return "true";
			else
				return "false";
		}

		virtual std::string doTypeString() const {
			return "bit";
		}

		bool mValue;
	};

	class Number : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<Number> ptr;

		Number() : ValueBase(VTNumber), mValue(0.0) {}
		Number(double value) : ValueBase(VTNumber), mValue(value) {}

		bool operator==(const Number& other) const { return (mValue == other.mValue); }
		bool operator!=(const Number& other) const { return (mValue != other.mValue); }

		double getValue() const { return mValue; }
		void setValue(const double value) { mValue = value; }

	private:
		int compare(const ValueBase& other) const;

		std::string doJsonString() const {
			std::stringstream ss;
			ss << mValue;
			return ss.str();
		}

		virtual std::string doTypeString() const {
			return "num";
		}

		double mValue;
	};

	class String : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<String> ptr;

		String() : ValueBase(VTString), mValue("") {}
		String(const std::string& value) : ValueBase(VTString), mValue(value) {}

		bool operator==(const String& other) const { return (mValue == other.mValue); }
		bool operator!=(const String& other) const { return (mValue != other.mValue); }

		std::string getValue() const { return mValue; }
		void setValue(const std::string& value) { mValue = value; }

		// return a copy of the string with all control characters escaped
		static std::string escapeString(const std::string& str);

	private:
		int compare(const ValueBase& other) const;

		std::string doJsonString() const {
			std::stringstream ss;
			ss << "\"" << escapeString(mValue) << "\"";
			return ss.str();
		}

		virtual std::string doTypeString() const {
			return "str";
		}

		std::string mValue;
	};

	// this is a std::vector adapter to hold JSON Values.
	class Array : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<Array> ptr;
		typedef std::vector<Value> container_type;
		typedef container_type::value_type value_type;
		typedef container_type::reference reference;
		typedef container_type::const_reference const_reference;
		typedef container_type::size_type size_type;
		typedef container_type::const_iterator const_iterator;
		typedef container_type::iterator iterator;
		typedef container_type::difference_type difference_type;
		typedef container_type::const_reverse_iterator const_reverse_iterator;
		typedef container_type::reverse_iterator reverse_iterator;
		typedef container_type::allocator_type allocator_type;

		Array() : ValueBase(VTArray), mValue() {}

		Array& operator=(const Array& __x) {
			mValue = __x.mValue;
			return *this;
		}

		friend bool operator==(const Array&, const Array&);
		friend bool operator<(const Array&, const Array&);

		// iterator methods
		iterator begin() { return mValue.begin(); }

		const_iterator begin() const { return mValue.begin(); }

		iterator end() { return mValue.end(); }

		const_iterator end() const { return mValue.end(); }

		reverse_iterator rbegin() { return mValue.rbegin(); }

		const_reverse_iterator rbegin() const { return mValue.rbegin(); }

		reverse_iterator rend() { return mValue.rend(); }

		const_reverse_iterator rend() const { return mValue.rend(); }

		// capacity
		size_type size() const { return mValue.size(); }

		size_type max_size() const { return mValue.max_size(); }

		void resize(size_type __new_size, value_type __x = value_type()) {
			mValue.resize(__new_size, __x);
		}

		size_type capacity() const { return mValue.capacity(); }

		bool empty() const { return mValue.empty(); }

		void reserve(size_type __n) { mValue.reserve(__n); }

		// element access
		reference operator[](size_type __n) { return mValue[__n]; }

		const_reference operator[](size_type __n) const { return mValue[__n]; }

		reference at(size_type __n) { return mValue.at(__n); }

		const_reference at(size_type __n) const { return mValue.at(__n); }

		reference front() { return mValue.front(); }

		const_reference front() const { return mValue.front(); }

		reference back() { return mValue.back(); }

		const_reference back() const { return mValue.back(); }

		// modifiers
		void push_back(const value_type& __x) { mValue.push_back(__x); }

		void pop_back() { mValue.pop_back(); }

		iterator insert(iterator __position, const value_type& __x) {
			return mValue.insert(__position, __x);
		}

		void insert(iterator __position, size_type __n, const value_type& __x) {
			mValue.insert(__position, __n, __x);
		}

		template<typename _InputIterator>
		void insert(iterator __position, _InputIterator __first,
				_InputIterator __last) {
			mValue.insert(__position, __first, __last);
		}

		iterator erase(iterator __position) { return mValue.erase(__position); }

		iterator erase(iterator __first, iterator __last) {
			return mValue.erase(__first, __last);
		}

		void swap(Array& __x) { mValue.swap(__x.mValue); }

		void clear() { mValue.clear(); }

	private:
		int compare(const ValueBase& other) const;

		std::string doJsonString() const;

		virtual std::string doTypeString() const {
			return "arr";
		}

		container_type mValue;
	};

	// Array comparisons
	inline bool operator==(const Array& x, const Array& y) {
		return x.mValue == y.mValue;
	}

	inline bool operator<(const Array& x, const Array& y) {
		return x.mValue < y.mValue;
	}

	inline bool operator!=(const Array& x, const Array& y) {
		return !(x == y);
	}

	inline bool operator>(const Array& x, const Array& y) {
		return y < x;
	}

	inline bool operator<=(const Array& x, const Array& y) {
		return !(y < x);
	}

	inline bool operator>=(const Array& x, const Array& y) {
		return !(x < y);
	}

	// a std::map adapter representing a JSON Object
	class Object : public ValueBase {
	public:
		typedef std::tr1::shared_ptr<Object> ptr;
		typedef std::map<std::string, Value> container_type;
		typedef container_type::key_type key_type;
		typedef container_type::mapped_type mapped_type;
		typedef container_type::value_type value_type;
		typedef container_type::key_compare key_compare;
		typedef container_type::allocator_type allocator_type;
		typedef container_type::pointer pointer;
		typedef container_type::const_pointer const_pointer;
		typedef container_type::reference reference;
		typedef container_type::const_reference const_reference;
		typedef container_type::iterator iterator;
		typedef container_type::const_iterator const_iterator;
		typedef container_type::size_type size_type;
		typedef container_type::difference_type difference_type;
		typedef container_type::reverse_iterator reverse_iterator;
		typedef container_type::const_reverse_iterator const_reverse_iterator;

		Object() : ValueBase(VTObject), mValue() {}

		Object& operator=(const Object& __x) {
			mValue = __x.mValue;
			return *this;
		}

		friend bool operator==(const Object&, const Object&);
		friend bool operator<(const Object&, const Object&);

		// iterator methods
		iterator begin() { return mValue.begin(); }

		const_iterator begin() const { return mValue.begin(); }

		iterator end() { return mValue.end(); }

		const_iterator end() const { return mValue.end(); }

		reverse_iterator rbegin() { return mValue.rbegin(); }

		const_reverse_iterator rbegin() const { return mValue.rbegin(); }

		reverse_iterator rend() { return mValue.rend(); }

		const_reverse_iterator rend() const { return mValue.rend(); }

		// capacity
		size_type size() const { return mValue.size(); }

		size_type max_size() const { return mValue.max_size(); }

		bool empty() const { return mValue.empty(); }

		// element access
		mapped_type& operator[](const key_type& __k) { return mValue[__k]; }

		mapped_type& at(const key_type& __k) { return mValue.at(__k); }

		const mapped_type& at(const key_type& __k) const { return mValue.at(__k); }

		// modifiers
		std::pair<iterator, bool> insert(const value_type& __x) {
			return mValue.insert(__x);
		}

		iterator insert(iterator __position, const value_type& __x) {
			return mValue.insert(__position, __x);
		}

		template <typename _InputIterator>
		void insert(_InputIterator __first, _InputIterator __last) {
			mValue.insert(__first, __last);
		}

		void erase(iterator __position) { mValue.erase(__position); }

		size_type erase(const key_type& __x) { return mValue.erase(__x); }

		void erase(iterator __first, iterator __last) {
			mValue.erase(__first, __last);
		}

		void swap(Object& __x) { mValue.swap(__x.mValue); }

		void clear() { mValue.clear(); }

		// map operations
		iterator find(const key_type& __x) { return mValue.find(__x); }

		const_iterator find(const key_type& __x) const { return mValue.find(__x); }

		size_type count(const key_type& __x) const { return mValue.count(__x); }

		iterator lower_bound(const key_type& __x) { return mValue.lower_bound(__x); }

		const_iterator lower_bound(const key_type& __x) const { return mValue.lower_bound(__x); }

		iterator upper_bound(const key_type& __x) { return mValue.upper_bound(__x); }

		const_iterator upper_bound(const key_type& __x) const { return mValue.upper_bound(__x); }

		std::pair<iterator, iterator> equal_range(const key_type& __x) {
			return mValue.equal_range(__x);
		}

		std::pair<const_iterator, const_iterator>
		equal_range(const key_type& __x) const {
			return mValue.equal_range(__x);
		}

		// convenience methods

		// return true if this Object has a given key
		bool hasKey(const std::string& key) const;

		// retrieve the value of key, if key doesn't exist return default value
		Value get(const std::string& key, const Value& def) const;

	private:
		int compare(const ValueBase& other) const;

		std::string doJsonString() const;

		virtual std::string doTypeString() const {
			return "obj";
		}

		container_type mValue;
	};

	// Object comparisons
	inline bool operator==(const Object& x, const Object& y) {
		return x.mValue == y.mValue;
	}

	inline bool operator<(const Object& x, const Object& y) {
		return x.mValue < y.mValue;
	}

	inline bool operator!=(const Object& x, const Object& y) {
		return !(x == y);
	}

	inline bool operator>(const Object& x, const Object& y) {
		return y < x;
	}

	inline bool operator<=(const Object& x, const Object& y) {
		return !(y < x);
	}

	inline bool operator>=(const Object& x, const Object& y) {
		return !(x < y);
	}

	// runtime cast methods
	// based upon any_cast from boost::any
	template<typename ValueType_>
	ValueType_ * value_cast(Value * operand) {
//		return operand && operand->mValue->getType() == ValueType_().getType()
//			? &static_cast<ValueType_ *>(operand->mValue.get())
//			: 0;
//		return std::tr1::static_pointer_cast<ValueType_>(operand->mValue).get();
		return operand && operand->mValue->getType() == ValueType_().getType()
			? std::tr1::static_pointer_cast<ValueType_>(operand->mValue).get()
			: 0;
	}

	template<typename ValueType_>
    inline const ValueType_ * value_cast(const Value * operand) {
        return value_cast<ValueType_>(const_cast<Value *>(operand));
    }

	template<typename ValueType_>
	inline ValueType_ value_cast(Value & operand) {
		typedef BOOST_DEDUCED_TYPENAME boost::remove_reference<ValueType_>::type nonref;

		nonref * result = value_cast<nonref>(&operand);
        if(!result)
        	JSONRPC_EXCEPT(jsonrpc::Exception::ECBadCast, std::string("Failed conversion using value_cast").c_str())
        return *result;
	}

	template<typename ValueType_>
	inline const ValueType_ value_cast(const Value& operand) {
		return value_cast<ValueType_>(const_cast<Value&>(operand));
	}

	// template specializations for shared_ptr's
	// no exception is thrown so user needs to check for return.get() == 0 for bad cast.
	template<>
	inline std::tr1::shared_ptr<Null> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<Null>(operand.getValue());
	}

	template<>
	inline std::tr1::shared_ptr<Bool> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<Bool>(operand.getValue());
	}

	template<>
	inline std::tr1::shared_ptr<Number> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<Number>(operand.getValue());
	}

	template<>
	inline std::tr1::shared_ptr<String> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<String>(operand.getValue());
	}

	template<>
	inline std::tr1::shared_ptr<Array> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<Array>(operand.getValue());
	}

	template<>
	inline std::tr1::shared_ptr<Object> value_cast(Value & operand) {
		return std::tr1::dynamic_pointer_cast<Object>(operand.getValue());
	}
}

#endif /* JSONRPC_VALUE_H_ */
