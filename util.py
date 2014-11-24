
import time, logging
from kazoo.client import KazooClient

def handleTimeout(func, timeout, *params, **paramMap):
    interval = 0.6
    if type(timeout) == tuple:
        timeout, interval = timeout
    rst = None
    while timeout > 0:
        t = time.time()
        rst = func(*params, **paramMap)
        if rst and not _isExcept(rst):
            break
        time.sleep(interval)
        timeout -= time.time() - t
    return rst

def _isExcept(e, eType = Exception):
    return isinstance(e, eType)


class ZkOpers(object):
    
    zk = None
    
    rootPath = "/letv/docker"
    
    '''
    classdocs
    '''
    def __init__(self,zkAddress,zkPort):
        '''
        Constructor
        '''
        self.zk = KazooClient(hosts=zkAddress+':'+str(zkPort))
        self.zk.start()

    def getClusterUUID(self):
        logging.debug(self.rootPath)
        dataNodeName = self.zk.get_children(self.rootPath)
        logging.debug(dataNodeName)
        return dataNodeName[0]

    def _retrieveSpecialPathProp(self,path):
        logging.debug(path)
        
        data = None
        
        if self.zk.exists(path):
            data,stat = self.zk.get(path)
            
        logging.debug(data)
        
        resultValue = {}
        if data != None and data != '':
            resultValue = eval(data)
        return resultValue

    def retrieve_container_cluster_info(self, containerClusterName):
        clusterUUID = self.getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/container/cluster/" + containerClusterName
        return self._retrieveSpecialPathProp(path)
    
    def check_create_cluster_flag(self, containerClusterName):
        cluster_info = self.retrieve_container_cluster_info(containerClusterName)
        create_ret = cluster_info.get('start_flag')
        if create_ret and create_ret == 'succeed':
            return True
