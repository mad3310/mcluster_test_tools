#coding:gbk

from auto import autoutil
from configobj import ConfigObj as co

log = autoutil.Logger(r'log\trace.log')
conf_ini = co('conf.ini')