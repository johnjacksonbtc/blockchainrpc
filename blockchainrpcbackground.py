import queue
import json
import time

def blockingrpcsyncerloop(requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets):
    while True:
        if not requestrpcjobpusher.is_alive():
            try:
                requestrpcjobpusher.start()
            except RuntimeError:
                pass
        requestrpcsocketscount = len(requestrpcsockets)
        i = 0
        if requestrpcsocketscount:
            blockcountlist = []
            while i < requestrpcsocketscount:
                rpcsocketqueue, ipportpair, rpcauthpair = requestrpcsockets[i]
                blockcounthandle = queue.Queue()
                requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblockcount"}', blockcounthandle))
                rpcstatus, rpcdata = blockcounthandle.get()
                try:
                    if rpcstatus == b'received':
                        blockcount = json.loads(rpcdata.decode())['result']
                        if blockcount != None:
                            blockcountlist += [(requestrpcsockets[i], blockcount)]
                except json.decoder.JSONDecodeError:
                    pass
                except KeyError:
                    pass
                i += 1
            requestrpcsocketscount = len(blockcountlist)
            if requestrpcsocketscount:
                lowestnode, lowestblockcount = blockcountlist[0]
                i = 1
                while i < requestrpcsocketscount:
                    node, blockcount = blockcountlist[i]
                    if blockcount < lowestblockcount:
                        lowestnode, lowestblockcount = node, blockcount
                    i += 1
                nextblockcountlist = []
                i = 0
                while i < requestrpcsocketscount:
                    node, blockcount = blockcountlist[i]
                    if lowestnode != node and lowestblockcount != blockcount:
                        nextblockcountlist += [(node, blockcount)]
                    i += 1
                potentialseednodecount = len(nextblockcountlist)
                if potentialseednodecount:
                    seednode, seedblockcount = nextblockcountlist[0]
                    i = 1
                    while i < potentialseednodecount:
                        node, blockcount = blockcountlist[i]
                        if blockcount < seedblockcount:
                            seednode, seedblockcount = node, blockcount
                        i += 1
                    seednoderpcsocketqueue, seednodeipportpair, seednoderpcauthpair = seednode
                    lowestnoderpcsocketqueue, lowestnodeipportpair, lowestnoderpcauthpair = lowestnode
                    i = lowestblockcount
                    try:
                        nofailures = True
                        while i >= 0:
                            seedblockhashhandle = queue.Queue()
                            requestrpcjobqueue.put((seednoderpcsocketqueue, seednodeipportpair, seednoderpcauthpair, b'{"jsonrpc": "1.0", "method": "getblockhash", "params": [' + str(i).encode() + b']}', seedblockhashhandle))
                            lowestblockhashhandle = queue.Queue()
                            requestrpcjobqueue.put((lowestnoderpcsocketqueue, lowestnodeipportpair, lowestnoderpcauthpair, b'{"jsonrpc": "1.0", "method": "getblockhash", "params": [' + str(i).encode() + b']}', lowestblockhashhandle))
                            seedrpcstatus, seedrpcdata = seedblockhashhandle.get()
                            lowestrpcstatus, lowestrpcdata = lowestblockhashhandle.get()
                            if seedrpcstatus == b'received' and lowestrpcstatus == b'received':
                                if json.loads(seedrpcdata.decode())['result'] == json.loads(lowestrpcdata.decode())['result']:
                                    break
                                elif not i:
                                    nofailures = False
                                    print('blockingrpcsyncerloop: genesis mismatch ' + json.loads(seedrpcdata.decode())['result'].__repr__() + ' != ' + json.loads(lowestrpcdata.decode())['result'].__repr__())
                                    break
                                else:
                                    i -= 1
                            else:
                                nofailures = False
                                break
                        if nofailures:
                            i += 1
                            while i <= seedblockcount:
                                getblockhashresult = b''
                                getblockhashhandle = queue.Queue()
                                requestrpcjobqueue.put((seednoderpcsocketqueue, seednodeipportpair, seednoderpcauthpair, b'{"jsonrpc": "1.0", "method": "getblockhash", "params": [' + str(i).encode() + b']}', getblockhashhandle))
                                getblockhashrpcstatus, getblockhashrpcdata = getblockhashhandle.get()
                                if getblockhashrpcstatus == b'received':
                                    getblockhashresult = json.loads(getblockhashrpcdata.decode())['result'].encode()
                                getblockhandle = queue.Queue()
                                getblockresult = b''
                                if getblockhashresult:
                                    requestrpcjobqueue.put((seednoderpcsocketqueue, seednodeipportpair, seednoderpcauthpair, b'{"jsonrpc": "1.0", "method": "getblock", "params": ["' + getblockhashresult + b'", false]}', getblockhandle))
                                    getblockrpcstatus, getblockrpcdata = getblockhandle.get()
                                    if getblockrpcstatus == b'received':
                                        getblockresult = json.loads(getblockrpcdata.decode())['result'].encode()
                                submitblockhandle = queue.Queue()
                                submitblocksuccessful = False
                                if getblockresult:
                                    requestrpcjobqueue.put((lowestnoderpcsocketqueue, lowestnodeipportpair, lowestnoderpcauthpair, b'{"jsonrpc": "1.0", "method": "submitblock", "params": ["' + getblockresult + b'"]}', submitblockhandle))
                                    submitblockstatus, x = submitblockhandle.get()
                                    if submitblockstatus == b'received':
                                        submitblocksuccessful = True
                                if not submitblocksuccessful:
                                    break
                                i += 1
                    except json.decoder.JSONDecodeError:
                        pass
                    except KeyError:
                        pass
                    except AttributeError:
                        pass
                    except TypeError:
                        pass
        time.sleep(60)
