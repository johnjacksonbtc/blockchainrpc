import sys
import socket
import threading
import queue
import base64
import json
import time

# Import specific application methods
import blockchainrpcnetworking
import blockchainrpcprocessing
import blockchainrpcserver
import blockchainrpcbackground

# Create global variables
readheadersjobqueue = queue.Queue()
readheadersjobworkers = []
readheadersjobpusher = threading.Thread(target = blockchainrpcprocessing.blockingreadheaderspusherloop, args = (readheadersjobqueue, readheadersjobworkers))
processheadersjobqueue = queue.Queue()
processheadersjobworkers = []
processheadersjobpusher = threading.Thread(target = blockchainrpcprocessing.blockingprocessheaderspusherloop, args = (processheadersjobqueue, processheadersjobworkers))
readdatajobqueue = queue.Queue()
readdatajobworkers = []
readdatajobpusher = threading.Thread(target = blockchainrpcprocessing.blockingreaddatapusherloop, args = (readdatajobqueue, readdatajobworkers))
servercontentproviderjobqueue = queue.Queue()
servercontentproviderjobpusher = threading.Thread(target = blockchainrpcserver.blockingservercontentprovider, args = (servercontentproviderjobqueue, ))
serverjobqueue = queue.Queue()
serverjobworkers = []
serverjobpusher = threading.Thread(target = blockchainrpcprocessing.blockingserverpusherloop, args = (serverjobqueue, serverjobworkers))
requestrpcjobqueue = queue.Queue()
requestrpcjobworkers = []
requestrpcjobpusher = threading.Thread(target = blockchainrpcprocessing.blockingrequestrpcpusherloop, args = (requestrpcjobqueue, requestrpcjobworkers))
requestrpcsockets = []
acceptthreadlist = []
# Bitcoin Core - addrindex
requestrpcsockets += [(queue.Queue(), (socket.AF_INET, '127.0.0.1', 8332), ('rpcuser', 'rpcpassword'))]
# Bitcoin Unlimited
# requestrpcsockets += [(queue.Queue(), (socket.AF_INET, '127.0.0.1', 8342), ('rpcuser', 'rpcpassword'))]
# Bitcoin Unlimited ipv6
# requestrpcsockets += [(queue.Queue(), (socket.AF_INET6, '0:0:0:0:0:0:0:1', 8342), ('rpcuser', 'rpcpassword'))]
sendresponsejobqueue = queue.Queue()
sendresponsejobworkers = []
sendresponsejobpusher = threading.Thread(target = blockchainrpcprocessing.blockingsendresponsepusherloop, args = (sendresponsejobqueue, sendresponsejobworkers))
incomingsocketrecyclequeue = queue.Queue()
serveraddresslist = []
serveraddresslist += [(socket.AF_INET, '127.0.0.1', 80)]
serveraddresslist += [(socket.AF_INET6, '0:0:0:0:0:0:0:1', 80)]
serveraddresslistlen = len(serveraddresslist)
i = 0
while i < serveraddresslistlen:
    serveraddressfamily, serveraddress, serverport = serveraddresslist[i]
    acceptthread = threading.Thread(target = blockchainrpcnetworking.blockingacceptloop, args = (serveraddressfamily, serveraddress, serverport, incomingsocketrecyclequeue))
    acceptthreadlist += [acceptthread]
    i += 1
blockingrpcsyncerloopthread = threading.Thread(target = blockchainrpcbackground.blockingrpcsyncerloop, args = (requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets)).start()

# Start accept connection blocking infinite loop on main thread
while True:
    i = 0
    acceptthreadlistlen = len(acceptthreadlist)
    while i < acceptthreadlistlen:
        if not acceptthreadlist[i].is_alive():
            try:
                acceptthreadlist[i].start()
            except RuntimeError:
                pass
        i += 1
    client = incomingsocketrecyclequeue.get()
    if not readheadersjobpusher.is_alive():
        try:
            readheadersjobpusher.start()
        except RuntimeError:
            pass
    print(client.__repr__() + ' on main loop')
    readheadersjobqueue.put((client, (processheadersjobqueue, processheadersjobpusher, ((readdatajobqueue, readdatajobpusher), (servercontentproviderjobqueue, servercontentproviderjobpusher, ((serverjobqueue, serverjobpusher, ((requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets),)),)), (sendresponsejobqueue, sendresponsejobpusher, incomingsocketrecyclequeue)))))
    #print('readdatajobpusher), (servercontentproviderjobqueue, servercontentproviderjobpusher, ((serverjobqueue, serverjobpusher, ((requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets),)),)), (sendresponsejobqueue, sendresponsejobpusher, incomingsocketrecyclequeue)) = ' + ((readdatajobqueue, readdatajobpusher), (servercontentproviderjobqueue, servercontentproviderjobpusher, ((serverjobqueue, serverjobpusher, ((requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets),)),)), (sendresponsejobqueue, sendresponsejobpusher, incomingsocketrecyclequeue)).__repr__())
