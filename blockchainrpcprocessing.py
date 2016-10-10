import queue
import threading
import blockchainrpcnetworking
import blockchainrpcserver

def blockingreadheadersloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingreadheadersloop wait')
        client, futurejobs = jobqueue.get()
        print(client.__repr__() + ' on blockingreadheadersloop')
        #print('blockingreadheadersloop got (' + client.__repr__() + ', ' + futurejobs.__repr__() + ')')
        blockchainrpcnetworking.blockingreadheaders(client, futurejobs)

def blockingreadheaderspusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingreadheaderspusherloop wait')
        client, futurejobs = jobqueue.get()
        print(client.__repr__() + ' on blockingreadheaderspusherloop')
        #print('blockingreadheaderspusherloop got (' + client.__repr__() + ', ' + futurejobs.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((client, futurejobs))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 64:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingreadheadersloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((client, futurejobs))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((client, futurejobs))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcnetworking.blockingreadheaders(client, futurejobs)
            
def blockingprocessheadersloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingprocessheadersloop wait')
        client, receivedheaderslist, nextjobgroup = jobqueue.get()
        print(client.__repr__() + ' on blockingprocessheadersloop')
        #print('blockingprocessheadersloop got (' + client.__repr__() + ', ' + receivedheaderslist.__repr__() + ',' + nextjobgroup.__repr__() + ')')
        blockchainrpcserver.blockingprocessheaders(client, receivedheaderslist, nextjobgroup)

def blockingprocessheaderspusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingprocessheaderspusherloop wait')
        client, receivedheaderslist, nextjobgroup = jobqueue.get()
        print(client.__repr__() + ' on blockingprocessheadersloop')
        #print('blockingprocessheaderspusherloop got (' + client.__repr__() + ', ' + receivedheaderslist.__repr__() + ',' + nextjobgroup.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((client, receivedheaderslist, nextjobgroup))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 32:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingprocessheadersloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((client, receivedheaderslist, nextjobgroup))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((client, receivedheaderslist, nextjobgroup))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcserver.blockingprocessheaders(client, receivedheaderslist, nextjobgroup)
            
def blockingreaddataloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingreaddataloop wait')
        client, length, backlinkqueue = jobqueue.get()
        print(client.__repr__() + ' on blockingreaddataloop')
        #print('blockingreaddataloop got (' + client.__repr__() + ', ' + length.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        blockchainrpcnetworking.blockingreaddata(client, length, backlinkqueue)

def blockingreaddatapusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingreaddatapusherloop wait')
        client, length, backlinkqueue = jobqueue.get()
        print(client.__repr__() + ' on blockingreaddatapusherloop')
        #print('blockingreaddatapusherloop got (' + client.__repr__() + ', ' + length.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((client, length, backlinkqueue))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 64:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingreaddataloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((client, length, backlinkqueue))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((client, length, backlinkqueue))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcnetworking.blockingreaddata(client, length, backlinkqueue)
   
def blockingrequestrpcloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingrequestrpcloop wait')
        rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue = jobqueue.get()
        #print('blockingrequestrpcloop got (' + rpcsocketqueue.__repr__() + ', ' + ipportpair.__repr__() + ',' + rpcauthpair.__repr__() + ',' + jsondata.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        blockchainrpcnetworking.blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue)

def blockingrequestrpcpusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingrequestrpcpusherloop wait')
        rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue = jobqueue.get()
        #print('blockingrequestrpcpusherloop got (' + rpcsocketqueue.__repr__() + ', ' + ipportpair.__repr__() + ',' + rpcauthpair.__repr__() + ',' + jsondata.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 4:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingrequestrpcloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcnetworking.blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue)

def blockingsendresponseloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingsendresponseloop wait')
        client, data, reuseconnection, backlinkqueue = jobqueue.get()
        print(client.__repr__() + ' on blockingsendresponseloop')
        #print('blockingsendresponseloop got (' + client.__repr__() + ', ' + data.__repr__() + ',' + reuseconnection.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        blockchainrpcnetworking.blockingsendresponse(client, data, reuseconnection, backlinkqueue)

def blockingsendresponsepusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingsendresponsepusherloop wait')
        client, data, reuseconnection, backlinkqueue = jobqueue.get()
        print(client.__repr__() + ' on blockingsendresponsepusherloop')
        #print('blockingsendresponsepusherloop got (' + client.__repr__() + ', ' + data.__repr__() + ',' + reuseconnection.__repr__() + ',' + backlinkqueue.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((client, data, reuseconnection, backlinkqueue))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 64:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingsendresponseloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((client, data, reuseconnection, backlinkqueue))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((client, data, reuseconnection, backlinkqueue))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcnetworking.blockingsendresponse(client, data, reuseconnection, backlinkqueue)
            
def blockingserverloop(jobqueue):

    # Start loop of blocking get and method
    while True:
        #print('blockingprocessheadersloop wait')
        uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue = jobqueue.get()
        #print('blockingprocessheadersloop got (' + client.__repr__() + ', ' + receivedheaderslist.__repr__() + ',' + nextjobgroup.__repr__() + ')')
        blockchainrpcserver.blockingserver(uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue)

def blockingserverpusherloop(jobqueue, workers):
    
    # Start loop of blocking get and put
    while True:
        #print('blockingprocessheaderspusherloop wait')
        uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue = jobqueue.get()
        #print('blockingprocessheaderspusherloop got (' + client.__repr__() + ', ' + receivedheaderslist.__repr__() + ',' + nextjobgroup.__repr__() + ')')
        jobpushed = False
        workerscount = len(workers)
        i = 0
        while i < workerscount:
            threadobject, queueobject = workers[i]
            if not threadobject.is_alive():
                try:
                    threadobject.start()
                except RuntimeError:
                    pass
            if queueobject.empty():
                queueobject.put((uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue))
                jobpushed = True
                break;
            i += 1
        if not jobpushed and workerscount < 16:
            newqueue = queue.Queue()
            newthread = threading.Thread(target = blockingserverloop, args = (newqueue,))
            newthread.start()
            workers += [(newthread, newqueue)]
            newqueue.put((uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue))
            jobpushed = True
        if not jobpushed and len(workers):
            workerscount = len(workers)
            bestthread, bestqueue = workers[0]
            bestqueuelength = bestqueue.qsize()
            i = 1
            while i < workerscount:
                newbestthread, newbestqueue = workers[i]
                newbestqueuelength = newbestqueue.qsize()
                if newbestqueuelength < bestqueuelength:
                    bestthread = newbestthread
                    bestqueue = newbestqueue
                    bestqueuelength = newbestqueuelength
                i += 1
            bestqueue.put((uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue))
            jobpushed = True
        if not jobpushed:

            # Run blocking method directly if no worker threads are started
            blockchainrpcserver.blockingserver(uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue)
            
