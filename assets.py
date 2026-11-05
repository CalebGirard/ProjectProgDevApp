import os
import customtkinter as ctk
import sys

class Assets:

    def __init__(self,dir):
        self.dir = dir
        self.assets = {}
        self.assets_list = []
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.current_dir = sys._MEIPASS
        else:
            self.current_dir = os.path.dirname(os.path.abspath(__file__))
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(self.current_dir,dir)):
            self.assets_list.extend(filenames)
            for f in filenames:
                self.assets[f] = os.path.join(dirpath,f)
            
    def getAssetPath(self,name):
        return self.assets.get(name)

    def getAssetPathList(self,nameList):
        return [ self.assets.get(name) for n in nameList ]