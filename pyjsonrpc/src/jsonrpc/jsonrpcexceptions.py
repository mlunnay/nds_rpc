# Copyright (c) 2008, Michael Lunnay <mlunnay@gmail.com.au>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Custom exception heirachy for jsonrpc."""

class JSONRPCError(Exception):
    def __init__(self, code, msg, data=None):
        self.code = code
        self.message = msg
        self.data = data
    
    def __str__(self):
        out = "JSON-RPCError(%d:%s)" % (self.code, self.message)
        if self.data:
            out += ": %s" % str(self.data)
        return out
    
    def json_equivalent(self):
        """return a json encodable object that represents this Exception."""

        obj = {'code': self.code, 'message': self.message}
        if self.data != None:
            obj['data'] = self.data
        
        return obj

class ParseError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32700, "Parse error", data)

class InvalidRequestError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32600, "Invalid Request", data)

class MethodNotFoundError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32601, "Method not found", data)

class InvalidParametersError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32602, "Invalid params", data)

class InternalError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32603, "Internal error", data)

class ApplicationError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32000, "Application error", data)

class JSONRPCAssertionError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32001, "Assertion error", data)

class JSONRPCNotImplementedError(JSONRPCError):
    def __init__(self, data=None):
        JSONRPCError.__init__(self, -32002, "Not Implemented", data)
