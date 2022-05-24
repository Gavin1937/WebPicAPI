
#######################################################################################
#                                                                                     #
#   URL Handler, wrapper of urllib.parse                                              #
#   get/search url path and edit url parameters                                       #
#   Requires Python 3.8 or above                                                      #
#                                                                                     #
#######################################################################################

from urllib.parse import ParseResult, urlparse, quote, unquote
from pathlib import PurePath
from typing import Union
from copy import deepcopy
import re


class urlHandler:
    
    def __init__(self, url:str):
        
        # private members
        self.__parseResult:ParseResult = urlparse(url)
        self.__path:PurePath = PurePath(self.__parseResult.path)
        self.__param:dict = dict()
        
        # parse parameters
        for p in self.__parseResult.query.split('&'):
            if p.count('=') != 1: # more than 1 '=', invalid parameter
                continue
            k,v = p.split('=')
            if k in self.__param: # duplicate parameter key, update value as list
                if type(self.__param.get(k)) is not list:
                    self.__param.update({k:[self.__param.get(k),v]})
                else: # type(self.__param.get(k)) is list
                    self.__param.get(k).append(v)
            else: # new parameter key
                self.__param.update({k:v})
    
    
    # accessor
    def getParseResult(self) -> ParseResult:
        return self.__parseResult
    
    def getPath(self) -> PurePath:
        return self.__path
    
    def getPathPart(self, idx:int) -> str:
        """
            get specific part of url path.\n
            Example:\n
                url = 'www.example.com/folder1/folder2/item/file'\n
                url_path = '/folder1/folder2/item/file'\n
                as a list: ['/', 'folder1', 'folder2', 'item', 'file']\n
                \n
                input parameter 'idx' will be use to retrieve element from the list\n
                0 will always return '/'\n
                \n
            :Param:\n
                idx => int index to retrieve element of path\n
            \n
            :Return:\n
                if idx is valid, return str value\n
                otherwise, throw IndexError\n
        """
        
        try:
            return self.__path.parts[idx]
        except IndexError as e: # bad idx
            e.args = ("Invalid url path idx.", )
            raise
    
    def getParam(self, use_unquote:bool=False) -> dict:
        """
            get url Parameter dictionary\n
            \n
            :Param:\n
                use_unquote => bool flag, whether decode input value with html url decoding\n
        """
        output = self.__param
        if use_unquote:
            for k,v in output.items():
                if type(v) is str:
                    output.update({k:unquote(v)})
                else:
                    for l in v:
                        output.update({k:unquote(l)})
        return self.__param
    
    def getParamAt(self, key:str, use_unquote:bool=False) -> Union[str,list]:
        """
            get specified url Parameter\n
            \n
            :Param:\n
                use_unquote => bool flag, whether decode input value with html url decoding\n
        """
        if use_unquote:
            v = self.__param.get(key)
            if type(v) is str:
                return unquote(v)
            else:
                for i,l in enumerate(v):
                    v[i] = unquote(l)
                return v
        return self.__param.get(key)
    
    def getDomain(self) -> str:
        return self.__parseResult.netloc
    
    def isPatternInPath(self, pattern:str) -> bool:
        "Whether input pattern in url path\n"
        
        return (str(self.__path).find(pattern) != -1)
    
    def isPatternInPathR(self, pattern:Union[str,re.Pattern]) -> bool:
        "Whether input Regex pattern in url path\n"
        
        match = re.search(pattern, str(self.__path))
        return (match != None)
    
    def isParamExists(self, key) -> bool:
        return (key in self.__param)
    
    def isValueList(self, key) -> bool:
        "is input key points to a list of values"
        
        return (
            self.isParamExists(key) and
            type(self.__param.get(key)) is list
        )
    
    def isPatternInDomain(self, pattern:str) -> bool:
        "Whether input pattern in url domain\n"
        
        return (pattern in self.__parseResult.netloc)
    
    def isPatternInDomainR(self, pattern:str) -> bool:
        "Whether input Regex pattern in url domain\n"
        
        match = re.search(pattern, self.__parseResult.netloc)
        return (match != None)
    
    
    # mutator
    def setParam(self, key:str, val:str, val_idx:int=0, use_quote:bool=True):
        """
            set url parameter with input val\n
            if key does not exists, function will add it to url parameters\n
            \n
            :Param:\n
                key       => str key of parameter\n
                val       => str new value of parameter\n
                val_val   => int index of value list (only for duplicate keys)\n
                            if input key points to a list,\n
                            function will use this parameter to edit the list element\n
                use_quote => bool flag, whether encode input value with html url encoding\n
        """
        
        if type(val) is not str:
            val = str(val)
        
        if use_quote:
            val = quote(val)
        
        try:
            # add new key & val if key does not exists
            if not self.isParamExists(key):
                self.__param.update({key:val})
            
            # key exists
            elif not self.isValueList(key): # edit value str
                self.__param.update({key:val})
            else: # edit value list
                self.__param.get(key)[val_idx] = val
            
            # update
            self.__parseResult = self.__parseResult._replace(query=self.__paramToStr())
            
        except Exception:
            raise
    
    def addParam(self, key:str, val:str, use_quote:bool=True):
        """
            add url parameter\n
            \n
            :Param:\n
                key       => str new key of parameter\n
                val       => str new value of parameter\n
                use_quote => bool flag, whether encode input value with html url encoding\n
        """
        
        if use_quote:
            val = quote(val)
        
        try:
            if not self.isParamExists(key): # new key
                self.__param.update({key:val})
            # duplicate key
            elif self.isValueList(key): 
                self.__param.get(key).append(val)
            else: # value is not list
                self.__param.update({key:[self.__param.get(key),val]})
            
            # update
            self.__parseResult = self.__parseResult._replace(query=self.__paramToStr())
            
        except Exception:
            raise
    
    def removeParam(self, key:str, val_idx:int=0):
        """
            remove url parameter\n
            \n
            :Param:\n
                key      => str key of parameter to remove\n
                val_idx  => int index (only for value list), default 0\n
        """
        
        try:
            if self.isParamExists(key):
                if not self.isValueList(key):
                    self.__param.pop(key)
                else: # self.isValueList(key)
                    self.__param.get(key).pop(val_idx)
                
                # update
                self.__parseResult = self.__parseResult._replace(query=self.__paramToStr())
                
        except IndexError as e:
            e.args = (f"Invalid val_idx for key: {key}")
            raise
    
    def clearParam(self):
        "Return a copy of urlHandler without url parameter."
        
        cp = self.copy()
        cp.__param = {}
        cp.__parseResult = cp.__parseResult._replace(query='')
        
        return cp
    
    def setPath(self, path:Union[str,PurePath]):
        """
            overwrite url path with input path\n
            \n
            :Param:\n
                path => str | PurePath of new path\n
        """
        
        if isinstance(path, PurePath):
            path = str(path)
        
        if path[0] != '/':
            path = '/' + path
        
        # update
        self.__parseResult = self.__parseResult._replace(path=path)
        self.__path = PurePath(path)
    
    
    # other functions
    def toString(self) -> str:
        return self.__parseResult.geturl()
    
    def copy(self):
        "deep copy current object"
        return deepcopy(self)
    
    
    # private helper function
    def __paramToStr(self) -> str:
        
        output = []
        for k,v in self.__param.items():
            if type(v) is str:
                output.append(f"{k}={v}")
            elif type(v) is list:
                for d in v:
                    output.append(f"{k}={d}")
        
        return "&".join(output) 
    

