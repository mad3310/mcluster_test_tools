#coding:gbk

import vagrant_vm
from optparse import OptionParser as OP

parser = OP(usage="%prog [Options]", version="%prog 1.0\nCopyright (C) 2014 by mcluster")
parser.add_option("-a", "--action", help=u"do vagrant action")
(options, args) = parser.parse_args()
action = options.action

vm = vagrant_vm.Vagrant()
if action == 'create':
    vm.create()

if action == 'up':
    vm.up()

if action == 'halt':
    vm.halt()

if action == 'destroy':
    vm.destroy()