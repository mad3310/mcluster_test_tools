#coding:gbk

import vagrant_cluster
from optparse import OptionParser as OP

parser = OP(usage="%prog [Options]", version="%prog 1.0\nCopyright (C) 2014 by mcluster")
parser.add_option("-a", "--action", help=u"do vagrant action")
(options, args) = parser.parse_args()
action = options.action

vc = vagrant_cluster.VagrantCluster()
if action == 'create':
    vc.create()

if action == 'up':
    vc.up()

if action == 'halt':
    vc.halt()

if action == 'destroy':
    vc.destroy()