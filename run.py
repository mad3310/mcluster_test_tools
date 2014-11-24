#!/usr/bin/env python

import os
import sys
import caseutil
import envutil
import util


def run(file_path):
    
    ret = util.handleTimeout(envutil.check_vm_stat, 3600)
    if not ret:
        return False  ##send mail
    return caseutil.run_cases(file_path)


if __name__ == '__main__':
    print run(r'/vagrant/case/test.json')
