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

import logging
import os.path
from jsonrpc import serviceProcedure, String, Number
from plugin import Plugin, implements
from servicepluginhandler import IRPCService

import config

class RPCLogging(Plugin):
    """This is a JSON-RPC service that provides logging functionality.
    
    As well as exposing rpc methods, it also provides configuration functions. 
    
    """
    
    _jsonrpcName = "logging"
    
    implements(IRPCService)
    
    def __init__(self, env):
        #setup logs from config file
        self.env = env
        self.config = env.config
        self.log = env.log
        
        # make sure the directory exists for the default log path
        path = self.config.get('logging', {}).get('default', {}).get('path', None)
        if path != None:
            path = os.path.dirname(path)
            if not os.path.exists(path):
                os.makedirs(path)
        
        self.logs = {}  # mapping between lognames and the file handler instance we auto create 
        
        for log in self.config.get('logging', {}).get('logs', {}):
            self.setup_log(log)

    @serviceProcedure(summary="Logs a message to the named logger with a given log level.",
                      params=[String('name'), Number('level'), String('message')],
                      ret=None)
    def log(self, name, level, message):
        """Logs a message to the named logger with a given log level."""
        
        if not isinstance(name, (str, unicode)) and \
            not isinstance(level, (int, float)) and \
            not isinstance(message, (str, unicode)):
            # this method does not return so just finish
            return
        
        log = logging.getLogger(name)
        
        if log.handlers == []:
            self.setup_log(name)
        
        log.log(level, message)
    
    def setup_log(self, name):
        cfg = self.config.get('logging', {})
        logs = cfg.get('logs', {})
        
        loggercfg = None
        fmtcfg = None
        default = False
        if logs.has_key(name):
            loggercfg = logs[name].get('logger', None)
            fmtcfg = logs[name].get('formatter', None)
        
        if loggercfg == None:
            loggercfg = cfg.get('default', {}).get('logger', {})
            default = True
        if fmtcfg == None:
            fmtcfg = cfg.get('default', {}).get('formatter', {})
                
        if default:
            fname = os.path.join(loggercfg.get('path', '.'), '%s.log' % name)
            level = loggercfg.get('level', 30)
        else:
            fname = loggercfg.get('path', None)
            
            if fname == None:
                fname = os.path.join(cfg.get('default', {}).get('logger', {}).get('path', 'logs'), '%s.log' % name)
            else:   # make sure the directory for the file exists
                path = os.path.dirname(fname)
                if not os.path.exists(path):
                    os.makedirs(path)
            
            level = loggercfg.get('level', None)
            if level == None:
                level = cfg.get('default', {}).get('logger', {}).get('level', 30)
        
        mode = loggercfg.get('mode', 'a')
        
        if loggercfg.get('type', 0) == 0:
            handler = logging.FileHandler(fname, mode)
        else:
            maxbytes = loggercfg.get('maxbytes', 4096)
            buckupcount = loggercfg.get('buckupcount', 3)
            handler = logging.handlers.RotatingFileHandler(fname, mode, maxbytes, backupcount)
        
        fmt = fmtcfg.get('format', '%(asctime)s %(levelname)-8s %(message)s')
        datefmt = fmtcfg.get('dateformat', None)
        if datefmt == None:
            formatter = logging.Formatter(fmt)
        else:
            formatter = logging.Formatter(fmt, datefmt)
        
        handler.setFormatter(formatter)
        handler.setLevel(level)
        
        self.logs[name] = handler
        
        log = logging.getLogger(name)
        log.addHandler(handler)
    
    def reset_config(self):
        """Call this after the config has been changed to reconfigure the logs."""
        
        for name, hdlr in self.logs.iteritems():
            log = logging.getLogger(name)
            log.removeHandler(hdlr)
            self.setup_log(name)
