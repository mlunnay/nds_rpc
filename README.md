# JSON RPC Lbrary, Server and Nintendo DS test library
This is a multi part project for Remote Procedure Calls using JSON as the transport format, for copying and updating files to and logging from a Nintendo DS for homebrew development. This was to remove the requirement of removing the microSD card from the Nintendo DS, connecting it to the PC, copying files, then replacing the microSD card into the Nintendo DS.

The server side is made of a python JSON RPC library [pyjsonrpc](https://github.com/mlunnay/nds_rpc/tree/master/pyjsonrpc), and a development server [ndsdevelserver](https://github.com/mlunnay/nds_rpc/tree/master/ndsdevelserver) implemented in Python.

[jsonrpc](https://github.com/mlunnay/nds_rpc/tree/master/jsonrpc) is a C++ library for calling JSON RPC methods on the remote server via the Nintendo DS's WIFI. This requires DevkitARM, and [MinGW](http://www.mingw.org/) no Windows to build.
