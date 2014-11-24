
import json, traceback, commands, logging 
import global_varies, mail, check

conf_ini = global_varies.conf_ini

def get_case(file_path):
    f = open(file_path)
    content = f.read()
    f.close()
    cases = json.loads(content)
    return cases

def _get_case_result(curl):
    curl = ' %s 2>/dev/null' % curl
    ret = commands.getoutput(curl)
    print '_get_case_result result:',str(ret)
    return json.loads(ret)

def run_one_case(case):
    error_detail = ''
    if not isinstance(case, dict):
        error_detail = 'get a wrong case, please check!'
        return error_detail
    try: 
        curl = case.get('curl')
        expect_result = case.get('expect_result')
        init = case.get('init')
        check_function = case.get('check_function')
        print 'test: %s' % str(curl)
        ret = _get_case_result(curl)
        
        if expect_result:
            com_ret = check.compare_result(ret, expect_result)
            print 'compare reslut and expect_result: %s' % str(com_ret)
            if not com_ret:
                error_detail = r'interface: %s: \n test result: %s, expect result: %s' % (curl, str(ret),  str(expect_result) )
                print 'compare_result : %s' % str(error_detail)
                return error_detail
        
        if check_function:
            error_detail = getattr(check, check_function)()
            if error_detail:
                print 'check_function reslut: %s' % str(error_detail)
                return error_detail
            print 'check_function %s : pass' % check_function
    
    except:
        print str(traceback.format_exc())
        return str(traceback.format_exc())

def run_cases(file_path):
    try:
        case_index_list = []
        cases = get_case(file_path)
        for case_index in cases:
            case_index_list.append(case_index)
        case_index_list.sort()
        for case_index in case_index_list:
            case = cases.get(case_index)
            error_detail = run_one_case(case)
            if error_detail:
                mail.sendMail('auto interface notice', error_detail, priority='1')
                return False
        mail.sendMail('auto interface notice', 'pass')
        return True
    except:
        logging.error( str(traceback.format_exc()) )
        return False

if __name__ == '__main__':
    print get_case('/vagrant/case/test.json')