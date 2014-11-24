
import util
import global_varies

conf_ini = global_varies.conf_ini

def compare_result(expect_result, result):
    rst = True
    if len(expect_result) != len(result):
        rst = False
    for key, value in expect_result.items():
        if key not in result:
            rst = False
            break
        if value != result.get(key):
            rst = False
            break
    return rst

def check_create_status(timeout=(200, 2)):
    def _check():
        return zk.check_create_cluster_flag(cluster_name)
        
    node_ips = conf_ini.get('node_ips')
    node = node_ips[0]
    zk = util.ZkOpers(node ,2181)
    cluster_name = conf_ini.get('cluster_name')
    if not util.handleTimeout(_check, timeout):
        return 'Time out'