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

__all__ = ['FileTransfer', 'IDownloadManipulator', 'IUploadManipulator'
           'IListDir', 'makeDirectoryEntry']

import os
import stat
import zlib
import base64

from jsonrpc import serviceProcedure, String, Number, Boolean, Object, Array, ApplicationError, JSONRPCAssertionError
from plugin import Plugin, ExtensionPoint, Interface, implements
from crc16 import crc16
from servicepluginhandler import IRPCService

class IDownloadManipulator(Interface):
    """Extension point interface for plugins that need to do custom handling for file downloads."""
    
    def download(self, head, tail, rootpath):
        """Fetch the data to be sent.
        
        This should return a string with the data to be returned.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @param rootpath: A string with the local rootpath for the path of the request. 
        """
    
    def handles(self, head, tail):
        """Utility method to tell if the plugin handles a particular request.
        
        This will allow a plugin to only handle graphic files by only returning
        true if the file extension is .jpg, .png, etc.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @return: True if this plugin will handle the request, False otherwise. 
        """

class IUploadManipulator(Interface):
    """Extension point interface for plugins that need to do custom handling for file uploads."""
    
    def upload(self, head, tail, data, rootpath):
        """Handle the data sent to the server.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @param data: a string containing the data that is being uploaded.
        @param rootpath: A string with the local rootpath for the path of the request.
        """
    
    def handles(self, head, tail):
        """Utility method to tell if the plugin handles a particular request.
        
        This will allow a plugin to only handle graphic files by only returning
        true if the file extension is .jpg, .png, etc.
        
        @param head: A string with the requested path that precedes tail.
        @param tail: the requested path relative to rootpath.
        @return: True if this plugin will handle the request, False otherwise. 
        """

class IListDir(Interface):
    """Extension point interface for plugins that need to do custom handling for file uploads."""
    
    def listDir(self, head, tail, rootpath):
        """Return a directory listing of the requested path.
        
        @param path: the path to list.
        @param rootpath: A string with the local rootpath for the path of the request.
        @return: a sequence of dictionaries with keys name, size, isDir and readonly.
        
        """

def makeDirectoryEntry(name, size, isdir = False, readonly = False):
    """Utility class for returning a dictionary of directory content information."""
    
    out = {"name": name,
           "size": size,
           "isDir": isdir,
           "readonly": readonly
           }
    
    return out

class FileTransfer(Plugin):
    """This is a JSON-RPC service that provides download and uploading capabilities."""
    
    _jsonrpcName = "file"
    
    implements(IRPCService)
    
    download_plugins = ExtensionPoint(IDownloadManipulator)
    upload_plugins = ExtensionPoint(IUploadManipulator)
    listdir_plugins = ExtensionPoint(IListDir)
    
    @serviceProcedure(summary="This method is used to request a file from the server.",
                      params=[String('file'), Boolean('compress')],
                      ret=Object())
    def download(self, file, compress = False):
        """This method is used to request a file from the server.
        
        @param file: path of the file to download.
        @param compress: if True the contents of the file will be compressed
            with zlib before sending.
        @return: a JSON-RPC Object with keys data, crc, and compressed.
        
        """
        
        cfg = getConfig(file)
        dl_plugins = dict([[x.__class__.__name__, x] for x in self.download_plugins])
        for plugin in cfg['plugins']:
            if dl_plugins.has_key(plugin):
                plugin = dl_plugins[plugin]
                if plugin.handles(cfg['head'], cfg['tail']):
                    data = plugin.download(cfg['head'], cfg['tail'], cfg['rootpath'])
                    break
            else:
                self.log.debug("FileTransfer.download: Skipping plugin %s, not found" % plugin)
        else:   # default download handling, just send the file
            path = os.path.normpath(os.path.join(cfg['rootpath'], cfg['tail']))
            if not os.path.exists(path):
                raise ApplicationError('IOError: No such file or directory: %s' % file)
            if not os.isfile(path):
                raise ApplicationError('IOError: %s is a directory' % file)
            data = open(path, 'rb').read()
        
        # compute the crc of the data
        crc = crc16(data)
        
        # compress the data if so requested
        if compress:
            data = zlib.compress(data)
        
        # encode the data in base64
        data = base64.b64encode(data)
        
        return {'data': data, 'crc': crc}
    
    @serviceProcedure(summary="This method uploads a file to the server.",
                      params=[String('data'), Number('crc'), Boolean('compress')],
                      ret=None)
    def upload(self, filename, data, crc, compressed = False):
        """This method uploads a file to the server.
        
        @param filename: file name of the file to download.
        @param data: the contents of the file being uploaded in base64 format.
        @param crc: the CRC-16-IBM (CRC16) Cyclic Redundancy Check for the data.
        @param compressed: if True the data will be decompressed with zlib.
        
        """
        
        # decode the base64 encoded string
        data_ = base64.b64decode(data)
        # decompress the data if needed
        if compressed:
            data_ = zlib.decompress(data)
        
        # make sure we recieved what we were expecting by computing the crc value
        if crc16(data_) != crc:
            self.log.debug('FileTransfer.upload: crc values did not match for request %s' % filename)
            raise JSONRPCAssertionError('crc value does not match')
        
        cfg = getConfig(file)
        ul_plugins = dict([[x.__class__.__name__, x] for x in self.upload_plugins])
        for plugin in cfg['plugins']:
            if ul_plugins.has_key(plugin):
                plugin = ul_plugins[plugin]
                if plugin.handles(cfg['head'], cfg['tail']):
                    plugin.upload(cfg['head'], cfg['tail'], data_, cfg['rootpath'])
                    break
            else:
                self.log.debug("FileTransfer.upload: Skipping plugin %s, not found" % plugin)
        else:   # default upload handling, just save the data
            path = os.path.normpath(os.path.join(cfg['rootpath'], cfg['tail']))
            if not os.path.exists(path):
                raise ApplicationError('IOError: No such file or directory: %s' % filename)
            if not os.isfile(path):
                raise ApplicationError('IOError: %s is a directory' % filename)
            
            f = open(path, 'wb')
            f.write(data_)
            f.close()
    
    @serviceProcedure(summary="Returns a directory listing of the given path.",
                      params=[String('path')],
                      ret=Array())
    def listDir(self, path):
        """Returns a directory listing of the given path.
        
        @param dir: the directory to list the contents of.
        @return: An Array of Objects each one listing the contents of the directory.
            Each Object has the keys name, size,
            dir (if true object is a directory),
            and readonly (if true object is read-only).
        
        """
        
        cfg = getConfig(path)
        list_plugins = dict([[x.__class__.__name__, x] for x in self.listdir_plugins])
        for plugin in cfg['plugins']:
            if list_plugins.has_key(plugin):
                plugin = list_plugins[plugin]
                data = plugin.listDir(cfg['head'], cfg['tail'], cfg['rootpath'])
                break
            else:
                self.log.debug("FileTransfer.listDir: Skipping plugin %s, not found" % plugin)
        else:   # default listDir handling
            path = os.path.normpath(os.path.join(cfg['rootpath'], cfg['tail']))
            if not os.path.exists(path):
                raise ApplicationError('IOError: No such file or directory: %s' % path)
            if not os.isdir(path):
                raise ApplicationError('IOError: %s is not a directory' % path)
            
            out = []
            for i in os.listdir(path):
                name = i
                size = os.path.getsize(os.path.join(path, i))
                isdir = os.path.isdir(os.path.join(path, i))
                readonly = os.access(os.path.join(path, i), os.W_OK)
                out.append(makeDirectoryEntry(name, size, isdir, readonly))
                
            return out
            
    def getConfig(self, path):
        """Get the configuration for the supplied path.
        
        @param path: the requested file path.
        @return: A dictionary with the configuration values for the given path.
            It has the keys rootpath, readonly and plugin from the directory
            configuration as well as the keys head and tail that contain the
            configuration path and the remainder of the path relative to
            rootpath.
        
        """
        tpath = path
        if tpath == '':
            tpath = '/'
            
        cfg = self.config.get('file', {})
        pathcfg = {}
        head = path
        tail = ''
        for p in cfg.get('directories', {}):
            prefix = os.path.commonprefix((tpath, p))
            if prefix != '' and len(p) == len(prefix):
                pathcfg = cfg['directories'][p]
                head = prefix
                tail = tpath[len(prefix):]
                if tail[0] == '/':
                    tail = tail[1:]
                break
        
        out = {}
        
        if pathcfg.has_key('rootpath'):
            out['rootpath'] = pathcfg['rootpath']
        else:
            out['rootpath'] = cfg.get('rootpath', 'servdocs')
            head = '/'
            tail = tpath[1:]
        
        if not os.path.isabs(out['rootpath']):
            out['rootpath'] = os.path.abspath(out['rootpath'])
        
        out['readonly'] = pathcfg.get('readonly', False)
        out['plugins'] = pathcfg.get('plugins', [])
        out['head'] = head
        out['tail'] = tail
        
        return out
