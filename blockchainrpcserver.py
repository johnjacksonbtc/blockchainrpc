import queue
import json
import time
import base64
import inspect
    
def blockingserver(uriresource, postedcontent, headerparams, nextjobgroup, backlinkqueue):
    #print((uriresource, postedcontent, nextjobgroup, backlinkqueue).__repr__() + ' on blockingserver')
    livefirstactivity = [time.time()]
    livelastactivity = [time.time()]
    liveresponse = [None]
    backlinkqueue.put((livefirstactivity, livelastactivity, liveresponse))
    protocolstring, includebody = headerparams
    requestrpcjob, = nextjobgroup
    requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets = requestrpcjob
    uriresourcelen = len(uriresource)
    response = b''
    if uriresourcelen and uriresource[0:1] == b'/':
        requestrpcsocketscount = len(requestrpcsockets)
        i = 0
        responsecontainer = b''
        responsepart = b''
        lastresponsepart = b''
        while i < requestrpcsocketscount:
            rpcsocketqueue, ipportpair, rpcauthpair = requestrpcsockets[i]
            if not requestrpcjobpusher.is_alive():
                try:
                    requestrpcjobpusher.start()
                except RuntimeError:
                    pass
            status = b'not processed'
            bestblockhashhandle = queue.Queue()
            requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getbestblockhash", "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', bestblockhashhandle))
            livelastactivity[0] = time.time()
            rpcstatus, data = bestblockhashhandle.get()
            livelastactivity[0] = time.time()
            responsepart2 = b''
            if rpcstatus == b'received':
                try:
                    bestblockhash = json.loads(data.decode())['result'].encode()
                    blockhash = bestblockhash
                    blockhashstatus = b'ok'
                    j = 0
                    while j < 6:
                        blockrowhandle = queue.Queue()
                        rawblockrowhandle = queue.Queue()
                        if blockhashstatus != b'ok':
                            responsepart2 += b' <span style="color=red;">' + blockhashstatus + b'</span> <br/>'
                            break
                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblock", "params": ["' + blockhash + b'", true], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', blockrowhandle))
                        livelastactivity[0] = time.time()
                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblock", "params": ["' + blockhash + b'", false], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', rawblockrowhandle))
                        livelastactivity[0] = time.time()
                        rpcstatus2, data2 = blockrowhandle.get()
                        livelastactivity[0] = time.time()
                        rawrpcstatus2, rawdata2 = rawblockrowhandle.get()
                        livelastactivity[0] = time.time()
                        if rpcstatus2 == b'received':
                            data2jsonobject = json.loads(data2.decode())
                            rawblockhex = None
                            rawblockhexlen = 0
                            i_28 = 0
                            if rawrpcstatus2 != b'received':
                                rawblockbinary = None
                            else:
##                                time1_start = time.time()
                                v1_32 = json.loads(rawdata2.decode())
                                if v1_32['error'] != None:
                                    rawblockbinary = None
                                else:
                                    v1_36 = v1_32['result']
                                    rawblockhex = v1_36.encode()
                                    rawblockhexlen = len(rawblockhex)
                                    try:
                                        rawblockbinary = bytes.fromhex(v1_36)
                                    except ValueError:
                                        pass
                                    if (not rawblockhexlen) or (len(rawblockbinary) != (rawblockhexlen >> 1)):
                                        rawblockbinary = None
##                                time1_end = time.time()
##                                print('binary block creation took ' + str(time1_end - time1_start) + ' seconds')
                            blocksizestatus = b'not processed'
                            blocksize = b''
                            if rawblockbinary == None:
                                try:
                                    blocksize = str(data2jsonobject['result']['size']).encode()
                                    blocksizestatus = b'ok'
                                except KeyError:
                                    blocksizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocksizestatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blocksizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocksizestatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                            else:
                                blocksize = str(len(rawblockbinary)).encode()
                                blocksizestatus = b'ok'
                            blockheightstatus = b'not processed'
                            blockheight = b''
                            try:
                                blockheight = str(data2jsonobject['result']['height']).encode()
                                blockheightstatus = b'ok'
                            except KeyError:
                                blockheightstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                try:
                                    blockheightstatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                except TypeError:
                                    pass
                            except TypeError:
                                blockheightstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                try:
                                    blockheightstatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                except TypeError:
                                    pass
                            transactioncountstatus = b'not processed'
                            transactioncount = b''
                            minerrewardstatus = b'not processed'
                            minerreward = b''
                            if rawblockbinary == None:
                                try:
                                    transactioncount = str(len(data2jsonobject['result']['tx'])).encode()
                                    transactioncountstatus = b'ok'
                                    coinbasetransactionid = data2jsonobject['result']['tx'][0].encode()
                                    coinbasetransactionhandle = queue.Queue()
                                    requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + coinbasetransactionid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', coinbasetransactionhandle))
                                    livelastactivity[0] = time.time()
                                    rpcstatus3, data3 = coinbasetransactionhandle.get()
                                    livelastactivity[0] = time.time()
                                    if rpcstatus3 == b'received':
                                        try:
                                            data3jsonobject = json.loads(data3.decode())
                                            txinputcount = len(data3jsonobject['result']['vin'])
                                            k = 0
                                            coinbaseinputstatus = b'coinbase not found'
                                            coinbaseoutputvaluesatoshis = 0 
                                            txoutputcount = len(data3jsonobject['result']['vout'])
                                            while k < txoutputcount:
                                                coinbaseoutputvaluesatoshis += int(data3jsonobject['result']['vout'][k]['value'] * 100000000) # Float arithmetic nailed
                                                k += 1
                                            if txinputcount == 1:
                                                try:
                                                    col88x = data3jsonobject['result']['vin'][0]['coinbase']
                                                    coinbaseinputstatus = b'found'
                                                except KeyError:
                                                    pass
                                            else:
                                                coinbaseinputstatus = b'unexpected input count in coinbase transaction: ' + str(txinputcount).encode()
                                            if coinbaseinputstatus == b'found':
                                                v1_48 = coinbaseoutputvaluesatoshis
                                                minerreward = (str(v1_48//100000000)+'.'+str(v1_48%100000000//10000000)+str(v1_48%10000000//1000000)+str(v1_48%1000000//100000)+str(v1_48%100000//10000)+str(v1_48%10000//1000)+str(v1_48%1000//100)+str(v1_48%100//10)+str(v1_48%10)).encode()
                                                minerrewardstatus = b'ok'
                                            else:
                                                minerrewardstatus = coinbaseinputstatus 
                                        except json.decoder.JSONDecodeError:
                                            minerrewardstatus = b'could not interpret rpc json response, data3 = ' + data3.__repr__().encode()
                                        except KeyError:
                                            minerrewardstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                            try:
                                                minerrewardstatus = b'rpc json error message: ' + json.loads(data3.decode())['error']['message'].encode()
                                            except TypeError:
                                                pass
                                        except TypeError:
                                            minerrewardstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                            try:
                                                minerrewardstatus = b'rpc json error message: ' + json.loads(data3.decode())['error']['message'].encode()
                                            except TypeError:
                                                pass
                                except KeyError:
                                    transactioncountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactioncountstatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    transactioncountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactioncountstatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                            else:
                                try:
                                    i_36 = 80 #block header
                                    if rawblockbinary[i_36] == b'\xff'[0]:
                                        transactioncount = str(rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24) + rawblockbinary[i_36+5]*(1<<32) + rawblockbinary[i_36+6]*(1<<40) + rawblockbinary[i_36+7]*(1<<48) + rawblockbinary[i_36+8]*(1<<56)).encode()
                                        i_36 += 9
                                    elif rawblockbinary[i_36] == b'\xfe'[0]:
                                        transactioncount = str(rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24)).encode()
                                        i_36 += 5
                                    elif rawblockbinary[i_36] == b'\xfd'[0]:
                                        transactioncount = str(rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8)).encode()
                                        i_36 += 3
                                    else:
                                        transactioncount = str(rawblockbinary[i_36]).encode()
                                        i_36 += 1
                                    transactioncountstatus = b'ok'
                                    i_36 += 4 #first transaction version
                                    v1_36 = 0 #first transaction vin count
                                    if rawblockbinary[i_36] == b'\xff'[0]:
                                        v1_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24) + rawblockbinary[i_36+5]*(1<<32) + rawblockbinary[i_36+6]*(1<<40) + rawblockbinary[i_36+7]*(1<<48) + rawblockbinary[i_36+8]*(1<<56)
                                        i_36 += 9
                                    elif rawblockbinary[i_36] == b'\xfe'[0]:
                                        v1_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24)
                                        i_36 += 5
                                    elif rawblockbinary[i_36] == b'\xfd'[0]:
                                        v1_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8)
                                        i_36 += 3
                                    else:
                                        v1_36 = rawblockbinary[i_36]
                                        i_36 += 1
                                    j_36 = 0
                                    while j_36 < v1_36:
                                        i_36 += 32 #vin previous txid
                                        i_36 += 4 #vin previous txid index
                                        v1_40 = 0 #vin script len
                                        if rawblockbinary[i_36] == b'\xff'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24) + rawblockbinary[i_36+5]*(1<<32) + rawblockbinary[i_36+6]*(1<<40) + rawblockbinary[i_36+7]*(1<<48) + rawblockbinary[i_36+8]*(1<<56)
                                            i_36 += 9
                                        elif rawblockbinary[i_36] == b'\xfe'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24)
                                            i_36 += 5
                                        elif rawblockbinary[i_36] == b'\xfd'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8)
                                            i_36 += 3
                                        else:
                                            v1_40 = rawblockbinary[i_36]
                                            i_36 += 1
                                        i_36 += v1_40 #vin script
                                        i_36 += 4 #vin sequenceno
                                        j_36 += 1
                                    v2_36 = 0 #first transaction vout count
                                    if rawblockbinary[i_36] == b'\xff'[0]:
                                        v2_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24) + rawblockbinary[i_36+5]*(1<<32) + rawblockbinary[i_36+6]*(1<<40) + rawblockbinary[i_36+7]*(1<<48) + rawblockbinary[i_36+8]*(1<<56)
                                        i_36 += 9
                                    elif rawblockbinary[i_36] == b'\xfe'[0]:
                                        v2_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24)
                                        i_36 += 5
                                    elif rawblockbinary[i_36] == b'\xfd'[0]:
                                        v2_36 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8)
                                        i_36 += 3
                                    else:
                                        v2_36 = rawblockbinary[i_36]
                                        i_36 += 1
                                    j_36 = 0
                                    v3_36 = 0 #first transaction vout value sum aka miner reward
                                    while j_36 < v1_36:
                                        v3_36 += rawblockbinary[i_36] + rawblockbinary[i_36+1]*(1<<8) + rawblockbinary[i_36+2]*(1<<16) + rawblockbinary[i_36+3]*(1<<24) + rawblockbinary[i_36+4]*(1<<32) + rawblockbinary[i_36+5]*(1<<40) + rawblockbinary[i_36+6]*(1<<48) + rawblockbinary[i_36+7]*(1<<56)
                                        i_36 += 8
                                        v1_40 = 0 #vout script len
                                        if rawblockbinary[i_36] == b'\xff'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24) + rawblockbinary[i_36+5]*(1<<32) + rawblockbinary[i_36+6]*(1<<40) + rawblockbinary[i_36+7]*(1<<48) + rawblockbinary[i_36+8]*(1<<56)
                                            i_36 += 9
                                        elif rawblockbinary[i_36] == b'\xfe'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8) + rawblockbinary[i_36+3]*(1<<16) + rawblockbinary[i_36+4]*(1<<24)
                                            i_36 += 5
                                        elif rawblockbinary[i_36] == b'\xfd'[0]:
                                            v1_40 = rawblockbinary[i_36+1] + rawblockbinary[i_36+2]*(1<<8)
                                            i_36 += 3
                                        else:
                                            v1_40 = rawblockbinary[i_36]
                                            i_36 += 1
                                        i_36 += v1_40 #vout script
                                        j_36 += 1
                                    minerreward = (str(v3_36//100000000)+'.'+str(v3_36%100000000//10000000)+str(v3_36%10000000//1000000)+str(v3_36%1000000//100000)+str(v3_36%100000//10000)+str(v3_36%10000//1000)+str(v3_36%1000//100)+str(v3_36%100//10)+str(v3_36%10)).encode()
                                    minerrewardstatus = b'ok'
                                    # += 4 #locktime
                                except IndexError:
                                    minerrewardstatus = b'invalid raw block received'
                            blocktimestatus = b'not processed'
                            blocktime = b''
                            if rawblockbinary == None:
                                try:
                                    blocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data2jsonobject['result']['time'])).encode()
                                    blocktimestatus = b'ok'
                                except KeyError:
                                    blocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocktimestatus = b'rpc json error message: ' + data2jsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                            else:
                                i_32 = 4 #block version
                                i_32 += 32 #previous block hash
                                i_32 += 32 #merkle root
                                try:
                                    blocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(rawblockbinary[i_32] + rawblockbinary[i_32+1]*(1<<8) + rawblockbinary[i_32+2]*(1<<16) + rawblockbinary[i_32+3]*(1<<24))).encode()
                                    blocktimestatus = b'ok'
                                except IndexError:
                                    blocktimestatus += b'invalid raw block received'
                            responsepart3 = b''
                            if blockheightstatus == b'ok':
                                responsepart3 += b' <b>Block Height</b>: <a href="/getblockbyheight/' + blockheight + b'/">' + blockheight + b'</a>'
                            else:
                                responsepart3 += b' <b>Block Height</b>: <span style="color:red;">' + blockheightstatus + b'</span>'
                            responsepart3 += b' <a href="/getblockbyhash/' + blockhash + b'/">hash</a>'
                            if blocktimestatus == b'ok':
                                responsepart3 += b' <b>Time</b>: ' + blocktime
                            else:
                                responsepart3 += b' <b>Time</b>: <span style="color:red;">' + blocktimestatus + b'</span>'
                            if transactioncountstatus == b'ok':
                                responsepart3 += b' <b>Transaction Count</b>: ' + transactioncount
                            else:
                                responsepart3 += b' <b>Transaction Count</b>: <span style="color:red;">' + transactioncountstatus + b'</span>'
                            if minerrewardstatus == b'ok':
                                responsepart3 += b' <b>Miner Reward</b>: ' + minerreward
                            else:
                                responsepart3 += b' <b>Miner Reward</b>: <span style="color:red;">' + minerrewardstatus + b'</span>'
                            if blocksizestatus == b'ok':
                                responsepart3 += b' <b>Block Size</b>: ' + blocksize
                            else:
                                responsepart3 += b' <b>Block Size</b>: <span style="color:red;">' + blocksizestatus + b'</span>'
                            responsepart2 += responsepart3 + b' <br/>'
                            status = b'ok'
                            try:
                                blockhash = data2jsonobject['result']['previousblockhash'].encode()
                            except KeyError:
                                blockhashstatus = b'no previous block hash'
                        else:
                            status = b'rpc response delivery status: ' + rpcstatus2
                            break
                        j += 1
                except json.decoder.JSONDecodeError:
                    status = b'could not interpret rpc json response, data = ' + data.__repr__().encode()
                except KeyError:
                    status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                    try:
                        status = b'rpc json error message: ' + json.loads(data.decode())['error']['message'].encode()
                    except TypeError:
                        pass
                except TypeError:
                    status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                    try:
                        status = b'rpc json error message: ' + json.loads(data.decode())['error']['message'].encode()
                    except TypeError:
                        pass
                except AttributeError:
                    status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
            else:
                status = b'rpc response delivery status: ' + rpcstatus
            if status != b'ok':
                responsepart2 += b' <span style="color=red;">' + status + b'</span> <br/>'
            unescapedid = rpcsocketqueue.__repr__().encode()
            unescapedidlen = len(unescapedid)
            escapedid = b''
            i_j = 0
            while i_j < unescapedidlen:
                if unescapedid[i_j:i_j+1] == b'"':
                    escapedid += b'&quot;'
                elif unescapedid[i_j:i_j+1] == b'&':
                    escapedid += b'&amp;'
                elif unescapedid[i_j:i_j+1] == b"'":
                    escapedid += b'&apos;'
                elif unescapedid[i_j:i_j+1] == b'<':
                    escapedid += b'&lt;'
                elif unescapedid[i_j:i_j+1] == b'>':
                    escapedid += b'&gt;'
                else:
                    escapedid += unescapedid[i_j:i_j+1]
                i_j += 1
            col52family, ip, port = ipportpair
            responsepart = b' <b>Previous 6 blocks on endpoint ' + ip.encode() + b':' + str(port).encode() + b' bound to ' + escapedid + b'</b> <br/>' + responsepart2
            if responsepart == lastresponsepart:
                responsecontainer += b' <b><span style="color:green;">Duplicate content dropped from endpoint ' + ip.encode() + b':' + str(port).encode() + b'</span></b> <br/>'
            else:
                responsecontainer += responsepart
                lastresponsepart = responsepart
            i += 1
        i = 0
        responsepart = b''
        lastresponsepart = b''
        while i < requestrpcsocketscount:
            rpcsocketqueue, ipportpair, rpcauthpair = requestrpcsockets[i]
            if not requestrpcjobpusher.is_alive():
                try:
                    requestrpcjobpusher.start()
                except RuntimeError:
                    pass
            responsepart2 = b''
            if uriresource[0:len(b'/getblockbyheight/')] == b'/getblockbyheight/' or uriresource[0:len(b'/getblockbyhash/')] == b'/getblockbyhash/' or uriresource[0:len(b'/address/')] == b'/address/' or uriresource[0:len(b'/mempool/')] == b'/mempool/' or uriresource[0:len(b'/tx/')] == b'/tx/':
                blockhashstatus = b'not processed'
                blockhash = b''
                httpchoice = b'not processed'
                j = 0
                if uriresource[0:len(b'/getblockbyheight/')] == b'/getblockbyheight/':
                    httpchoice = b'block'
                    j = len(b'/getblockbyheight/')
                    blockheight = 0
                    while j < uriresourcelen:
                        if b'0'[0] <= uriresource[j] and uriresource[j] <= b'9'[0]:
                            blockheight = blockheight * 10 + uriresource[j] - b'0'[0]
                        elif uriresource[j:j+1] == b'/':
                            getblockbyheighthandle = queue.Queue()
                            requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblockhash", "params": [' + str(blockheight).encode() + b'], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', getblockbyheighthandle))
                            livelastactivity[0] = time.time()
                            rpcstatus, data = getblockbyheighthandle.get()
                            livelastactivity[0] = time.time()
                            if rpcstatus == b'received':
                                try:
                                    blockhash = json.loads(data.decode())['result'].encode()
                                    blockhashstatus = b'ok'
                                except json.decoder.JSONDecodeError:
                                    blockhashstatus = b'could not interpret rpc json response, data = ' + data.__repr__().encode()
                                except KeyError:
                                    blockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockhashstatus = b'rpc json error message: ' + json.loads(data.decode())['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockhashstatus = b'rpc json error message: ' + json.loads(data.decode())['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except AttributeError:
                                    blockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockhashstatus = b'rpc json error message: ' + json.loads(data.decode())['error']['message'].encode()
                                    except TypeError:
                                        pass
                            else:
                                blockhashstatus = b'rpc response delivery status: ' + rpcstatus
                            break
                        else:
                            blockhashstatus = b'invalid block height requested'
                            break
                        j += 1
                if uriresource[0:len(b'/getblockbyhash/')] == b'/getblockbyhash/':
                    httpchoice = b'block'
                    j = len(b'/getblockbyhash/')
                    blockhash = b''
                    while j < uriresourcelen:
                        if b'0'[0] <= uriresource[j] and uriresource[j] <= b'9'[0]:
                            blockhash += uriresource[j:j+1]
                        elif b'a'[0] <= uriresource[j] and uriresource[j] <= b'f'[0]:
                            blockhash += uriresource[j:j+1]
                        elif uriresource[j:j+1] == b'/':
                            blockhashstatus = b'ok'
                            break
                        else:
                            break
                        j += 1
                    if len(blockhash) != len(b'000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'):
                        blockhashstatus = b'invalid block hash requested'
                addressstatus = b'not processed'
                address = b''
                if uriresource[0:len(b'/address/')] == b'/address/':
                    httpchoice = b'address'
                    j = len(b'/address/')
                    while j < uriresourcelen:
                        if b'1'[0] <= uriresource[j] and uriresource[j] <= b'9'[0]:
                            address += uriresource[j:j+1]
                        elif b'A'[0] <= uriresource[j] and uriresource[j] <= b'H'[0]:
                            address += uriresource[j:j+1]
                        elif b'J'[0] <= uriresource[j] and uriresource[j] <= b'N'[0]:
                            address += uriresource[j:j+1]
                        elif b'P'[0] <= uriresource[j] and uriresource[j] <= b'Z'[0]:
                            address += uriresource[j:j+1]
                        elif b'a'[0] <= uriresource[j] and uriresource[j] <= b'k'[0]:
                            address += uriresource[j:j+1]
                        elif b'm'[0] <= uriresource[j] and uriresource[j] <= b'z'[0]:
                            address += uriresource[j:j+1]
                        elif uriresource[j:j+1] == b'/':
                            addressstatus = b'ok'
                            break
                        else:
                            break
                        j += 1
                mempoolstatus = b'not processed'
                if uriresource[0:len(b'/mempool/')] == b'/mempool/':
                    httpchoice = b'mempool'
                    j = len(b'/mempool/') - 1
                    mempoolstatus = b'ok'
                requestedtxarray = []
                lastrequestedtx = b''
                while j < uriresourcelen:
                    if uriresource[j:j+len(b'/tx/')] == b'/tx/':
                        lastrequestedtx = b''
                        j += len(b'/tx/')
                        while j < uriresourcelen:
                            if b'0'[0] <= uriresource[j] and uriresource[j] <= b'9'[0]:
                                lastrequestedtx += uriresource[j:j+1]
                            elif b'a'[0] <= uriresource[j] and uriresource[j] <= b'f'[0]:
                                lastrequestedtx += uriresource[j:j+1]
                            else:
                                break
                            j += 1
                        if len(lastrequestedtx) == len(b'4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'):
                            requestedtxarray += [lastrequestedtx]
                    else:
                        break
##                tracebackcommand = None
##                if uriresource[j:j+len(b'/traceback/locaterequested/')] == b'/traceback/locaterequested/':
##                    tracebackcommand = b'locaterequested'
##                elif uriresource[j:j+len(b'/traceback/locatereturned/')] == b'/traceback/locatereturned/':
##                    tracebackcommand = b'locatereturned'
##                elif uriresource[j:j+len(b'/traceback/locateall/')] == b'/traceback/locateall/':
##                    tracebackcommand = b'locateall'
##                elif uriresource[j:j+len(b'/traceback/locaterequesteddeps/')] == b'/traceback/locaterequesteddeps/':
##                    tracebackcommand = b'locaterequesteddeps'
##                elif uriresource[j:j+len(b'/traceback/locatereturneddeps/')] == b'/traceback/locatereturneddeps/':
##                    tracebackcommand = b'locatereturneddeps'
##                elif uriresource[j:j+len(b'/traceback/locatealldeps/')] == b'/traceback/locatealldeps/':
##                    tracebackcommand = b'locatealldeps'
##                elif uriresource[j:j+len(b'/traceback/tracebackrequested/')] == b'/traceback/tracebackrequested/':
##                    tracebackcommand = b'tracebackrequested'
##                elif uriresource[j:j+len(b'/traceback/tracebackreturned/')] == b'/traceback/tracebackreturned/':
##                    tracebackcommand = b'tracebackreturned'
##                elif uriresource[j:j+len(b'/traceback/tracebackall/')] == b'/traceback/tracebackall/':
##                    tracebackcommand = b'tracebackall'
##                elif uriresource[j:j+len(b'/traceback/tracebackrequesteddeps/')] == b'/traceback/tracebackrequesteddeps/':
##                    tracebackcommand = b'tracebackrequesteddeps'
##                elif uriresource[j:j+len(b'/traceback/tracebackreturneddeps/')] == b'/traceback/tracebackreturneddeps/':
##                    tracebackcommand = b'tracebackreturneddeps'
##                elif uriresource[j:j+len(b'/traceback/tracebackalldeps/')] == b'/traceback/tracebackalldeps/':
##                    tracebackcommand = b'tracebackalldeps'
                requestedtxmap = {}
                for requestedtxindex, requestedtxid in enumerate(requestedtxarray):
                    requestedtxmap[requestedtxid] = requestedtxindex
                responsepart2 = b''
                returnedtxlist = []
                rawblockbinary = b''
                rawblockhex = None
                rawblockindex = 0
                if httpchoice == b'block':
                    print('httpchoice block hit')
                    blockhashquerystatus = b'no errors'
                    if blockhashstatus == b'ok':
                        blockhashqueryhandle = queue.Queue()
                        rawblockhashqueryhandle = queue.Queue()
                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblock", "params": ["' + blockhash + b'", true], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', blockhashqueryhandle))
                        livelastactivity[0] = time.time()
                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getblock", "params": ["' + blockhash + b'", false], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', rawblockhashqueryhandle))
                        livelastactivity[0] = time.time()
                        rpcstatus, data = blockhashqueryhandle.get()
                        livelastactivity[0] = time.time()
                        rawblockrpcstatus, rawblockdata = rawblockhashqueryhandle.get()
                        livelastactivity[0] = time.time()
                        if rpcstatus == b'received':
                            try:
                                rawblockbinary = b''
                                rawblockhex = None
                                i_32 = 0
                                if rawblockrpcstatus != b'received':
                                    rawblockbinary = None
                                else:
                                    v1_36 = json.loads(rawblockdata.decode())
                                    if v1_36['error'] != None:
                                        rawblockbinary = None
                                    else:
                                        v1_40 = json.loads(rawblockdata.decode())['result']
                                        rawblockhex = v1_40.encode()
                                        try:
                                            rawblockbinary = bytes.fromhex(rawblockhex.decode())
                                        except ValueError:
                                            rawblockbinary = None
                                        if len(rawblockbinary) != (len(rawblockhex)>>1) or (not rawblockhex):
                                            rawblockbinary = None
                                datajsonobject = json.loads(data.decode())
                                blockrawheaderstatus = b'not processed'
                                blockrawheader = b''
                                if rawblockbinary == None:
                                    blockrawheaderstatus = b'raw block not available'
                                else:
                                    try:
                                        blockrawheader = rawblockhex[0:80*2]
                                        blockrawheaderstatus = b'ok'
                                    except IndexError:
                                        blockrawheaderstatus = b'invalid raw block received'
                                blockconfirmationsstatus = b'not processed'
                                blockconfirmations = b''
                                try:
                                    blockconfirmations = str(datajsonobject['result']['confirmations']).encode()
                                    blockconfirmationsstatus = b'ok'
                                except KeyError:
                                    blockconfirmationsstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockconfirmationsstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockconfirmationsstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockconfirmationsstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                blocksizestatus = b'not processed'
                                blocksize = b''
                                if rawblockbinary == None:
                                    try:
                                        blocksize = str(datajsonobject['result']['size']).encode()
                                        blocksizestatus = b'ok'
                                    except KeyError:
                                        blocksizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocksizestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blocksizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocksizestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    blocksize = str(len(rawblockbinary)).encode()
                                    blocksizestatus = b'ok'
                                blockheightstatus = b'not processed'
                                blockheight = b''
                                try:
                                    blockheight = str(datajsonobject['result']['height']).encode()
                                    blockheightstatus = b'ok'
                                except KeyError:
                                    blockheightstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockheightstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockheightstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockheightstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                blockversionstatus = b'not processed'
                                blockversion = b''
                                if rawblockbinary == None:
                                    try:
                                        blockversion = hex(datajsonobject['result']['version']).encode()
                                        blockversionstatus = b'ok'
                                    except KeyError:
                                        blockversionstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockversionstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blockversionstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockversionstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    try:
                                        blockversion = hex(rawblockbinary[0] + rawblockbinary[1]*(1<<8) + rawblockbinary[2]*(1<<16) + rawblockbinary[3]*(1<<24)).encode()
                                        blockversionstatus = b'ok'
                                    except IndexError:
                                        blockversionstatus = b'invalid raw block received'
                                blockmerklerootstatus = b'not processed'
                                blockmerkleroot = b''
                                if rawblockbinary == None:
                                    try:
                                        blockmerkleroot = datajsonobject['result']['merkleroot'].encode()
                                        blockmerklerootstatus = b'ok'
                                    except KeyError:
                                        blockmerklerootstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockmerklerootstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blockmerklerootstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockmerklerootstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    try:
                                        i_40 = 4 #block version
                                        i_40 += 32 #previous block hash
                                        j_40 = 0
                                        while j_40 < 32:
                                            blockmerkleroot += rawblockhex[(i_40 + 31 - j_40)*2:(i_40 + 32 - j_40)*2]
                                            j_40 += 1
                                        blockmerklerootstatus = b'ok'
                                    except IndexError:
                                        blockmerklerootstatus = b'invalid raw block received'
                                blocktxcountstatus = b'not processed'
                                blocktxcount = b''
                                blockminerrewardstatus = b'not processed'
                                blockminerreward = b''
                                blockcoinbasestatus = b'not processed'
                                blockcoinbase = b''
                                blocktxarray = []
                                try:
                                    blocktxcountinteger = len(datajsonobject['result']['tx'])
                                    blocktxcount = str(blocktxcountinteger).encode()
                                    blocktxcountstatus = b'ok'
                                    j = 0
                                    while j < blocktxcountinteger:
                                        foundtxid = datajsonobject['result']['tx'][j].encode()
                                        txisrequested = False
                                        try:
                                            x = requestedtxarray[requestedtxmap[foundtxid]]
                                            txisrequested = True
                                        except KeyError:
                                            pass
                                        if txisrequested:
                                            blocktxarray += [(foundtxid, queue.Queue())]
                                        else:
                                            blocktxarray += [(foundtxid,)]
                                        j += 1
                                except KeyError:
                                    blocktxcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocktxcountstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass            
                                except TypeError:
                                    blocktxcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocktxcountstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                returnedtxlist = blocktxarray[:]
                                if rawblockbinary == None:
                                    try:
                                        coinbasetxid = datajsonobject['result']['tx'][0].encode()
                                        coinbasetxqueue = queue.Queue()
                                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + coinbasetxid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', coinbasetxqueue))
                                        livelastactivity[0] = time.time()
                                        col40rpcstatus, col40data = coinbasetxqueue.get()
                                        livelastactivity[0] = time.time()
                                        col40status = b'no failures'
                                        if col40rpcstatus == b'received':
                                            coinbaseoutputvaluesatoshis = 0
                                            coinbaseoutputvaluestatus = b'not processed'
                                            unescapedcoinbase = b''
                                            unescapedcoinbasestatus = b'not processed'
                                            col44status = b'no failures'
                                            try:
                                                col48datajsonobject = json.loads(col40data.decode())
                                                try:
                                                    unescapedcoinbase = col48datajsonobject['result']['vin'][0]['coinbase'].encode()
                                                    unescapedcoinbasestatus = b'ok'
                                                    coinbaseoutputvaluesatoshis = 0
                                                    txoutputcount = len(col48datajsonobject['result']['vout'])
                                                    j = 0
                                                    while j < txoutputcount:
                                                        coinbaseoutputvaluesatoshis += int(col84datajsonobject['result']['vout'][j]['value'] * 100000000)
                                                        j += 1
                                                    coinbaseoutputvaluestatus = b'ok' 
                                                except TypeError:
                                                    col44status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                                    try:
                                                        col44status = b'rpc json error message: ' + col48datajsonobject['error']['message'].encode()
                                                    except TypeError:
                                                        pass 
                                                except KeyError:
                                                    col44status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                                    try:
                                                        col44status = b'rpc json error message: ' + col48datajsonobject['error']['message'].encode()
                                                    except TypeError:
                                                        pass
                                            except json.decoder.JSONDecodeError:
                                                col44status = b'could not interpret rpc json response, col76data = ' + col76data.__repr__().encode()
                                            except AttributeError:
                                                col44status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                            escapedcoinbase = b''
                                            if unescapedcoinbasestatus == b'ok':
                                                unescapedcoinbaselen = len(unescapedcoinbase)
                                                col48_i = 0
                                                col48status = b'no failures'
                                                while (col48_i + 1) < unescapedcoinbaselen:
                                                    col52byte = bytes.fromhex(unescapedcoinbase[col48_i:col48_i+2].decode())
                                                    if col52byte == b'"':
                                                        escapedcoinbase += b'&quot;'
                                                    elif col52byte == b'&':
                                                        escapedcoinbase += b'&amp;'
                                                    elif col52byte == b"'":
                                                        escapedcoinbase += b'&apos;'
                                                    elif col52byte == b'<':
                                                        escapedcoinbase += b'&lt;'
                                                    elif col52byte == b'>':
                                                        escapedcoinbase += b'&gt;'
                                                    elif b' ' <= col52byte and col52byte <= b'~':
                                                        escapedcoinbase += col52byte
                                                    elif col52byte != None:
                                                        escapedcoinbase += b'\\x' + unescapedcoinbase[col48_i:col48_i+2]
                                                    else:
                                                        col48status = b'unexpected response'
                                                        break
                                                    col48_i += 2
                                                if col48status == b'no failures':
                                                    unescapedcoinbasestatus = b'ok'
                                                else:
                                                    unescapedcoinbasestatus = col48status
                                            if unescapedcoinbasestatus == b'ok':
                                                blockcoinbase = escapedcoinbase
                                                blockcoinbasestatus = b'ok'
                                            else:
                                                blockcoinbasestatus = unescapedcoinbasestatus
                                            if coinbaseoutputvaluestatus == b'ok':
                                                v1_48 = coinbaseoutputvaluesatoshis
                                                blockminerreward = (str(v1_48//100000000)+'.'+str(v1_48%100000000//10000000)+str(v1_48%10000000//1000000)+str(v1_48%1000000//100000)+str(v1_48%100000//10000)+str(v1_48%10000//1000)+str(v1_48%1000//100)+str(v1_48%100//10)+str(v1_48%10)).encode()
                                                blockminerrewardstatus = b'ok'
                                            else:
                                                blockminerrewardstatus = coinbaseoutputvaluestatus
                                        else:
                                            col40status = b'rpc response delivery status: ' + col40rpcstatus
                                            blockcoinbasestatus = col40status
                                            blockminerrewardstatus = col40status            
                                    except KeyError:
                                        blocktxcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocktxcountstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass            
                                    except TypeError:
                                        blocktxcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocktxcountstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    try:
                                        #blocktxcount = b''
                                        #blockminerreward = b''
                                        #blockcoinbase = b''
                                        blockcoinbaseraw = b''
                                        j = 0
                                        i_40 = 80 #block header
                                        blocktxcountinteger = 0
                                        if rawblockbinary[i_40] == b'\xff'[0]:
                                            blocktxcountinteger = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                            i_40 += 9
                                        elif rawblockbinary[i_40] == b'\xfe'[0]:
                                            blocktxcountinteger = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                            i_40 += 5
                                        elif rawblockbinary[i_40] == b'\xfd'[0]:
                                            blocktxcountinteger = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                            i_40 += 3
                                        else:
                                            blocktxcountinteger = rawblockbinary[i_40]
                                            i_40 += 1
                                        blocktxcount = str(blocktxcountinteger).encode()
                                        blocktxcountstatus = b'ok'
                                        while j < 1: # < blocktxcountinteger:
                                            coinbtx = False
                                            i_40 += 4 #transaction version
                                            v1_44 = 0 #transaction vin count
                                            if rawblockbinary[i_40] == b'\xff'[0]:
                                                v1_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                                i_40 += 9
                                            elif rawblockbinary[i_40] == b'\xfe'[0]:
                                                v1_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                                i_40 += 5
                                            elif rawblockbinary[i_40] == b'\xfd'[0]:
                                                v1_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                                i_40 += 3
                                            else:
                                                v1_44 = rawblockbinary[i_40]
                                                i_40 += 1
                                            j_44 = 0
                                            while j_44 < v1_44:
                                                v1_48 = rawblockbinary[i_40:i_40+32]
                                                i_40 += 32 #vin previous txid
                                                v2_48 = rawblockbinary[i_40:i_40+4]
                                                i_40 += 4 #vin previous txid index
                                                v3_48 = 0 #vin script len
                                                if rawblockbinary[i_40] == b'\xff'[0]:
                                                    v3_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                                    i_40 += 9
                                                elif rawblockbinary[i_40] == b'\xfe'[0]:
                                                    v3_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                                    i_40 += 5
                                                elif rawblockbinary[i_40] == b'\xfd'[0]:
                                                    v3_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                                    i_40 += 3
                                                else:
                                                    v3_48 = rawblockbinary[i_40]
                                                    i_40 += 1
                                                if v1_48 == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' and v2_48 == b'\xff\xff\xff\xff':
                                                    blockcoinbaseraw += rawblockbinary[i_40:i_40+v3_48]
                                                    coinbtx = True
                                                else:
                                                    i_52 = 0
                                                    v1_48len = len(v1_48)
                                                    v1_52 = b''
                                                    while i_52 < v1_48len:
                                                        v1_52 += v1_48[v1_48len - 1 - i_52:v1_48len - i_52].hex().encode()
                                                        i_52 += 1
                                                i_40 += v3_48 #vin script sometimes coinbase
                                                i_40 += 4 #vin sequenceno
                                                j_44 += 1
                                            v2_44 = 0 #transaction vout count
                                            if rawblockbinary[i_40] == b'\xff'[0]:
                                                v2_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                                i_40 += 9
                                            elif rawblockbinary[i_40] == b'\xfe'[0]:
                                                v2_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                                i_40 += 5
                                            elif rawblockbinary[i_40] == b'\xfd'[0]:
                                                v2_44 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                                i_40 += 3
                                            else:
                                                v2_44 = rawblockbinary[i_40]
                                                i_40 += 1
                                            j_44 = 0
                                            v3_44 = 0 #transaction vout value sum sometimes miner reward
                                            while j_44 < v2_44:
                                                v3_44 += rawblockbinary[i_40] + rawblockbinary[i_40+1]*(1<<8) + rawblockbinary[i_40+2]*(1<<16) + rawblockbinary[i_40+3]*(1<<24) + rawblockbinary[i_40+4]*(1<<32) + rawblockbinary[i_40+5]*(1<<40) + rawblockbinary[i_40+6]*(1<<48) + rawblockbinary[i_40+7]*(1<<56)
                                                i_40 += 8
                                                v1_48 = 0 #vout script len
                                                if rawblockbinary[i_40] == b'\xff'[0]:
                                                    v1_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                                    i_40 += 9
                                                elif rawblockbinary[i_40] == b'\xfe'[0]:
                                                    v1_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                                    i_40 += 5
                                                elif rawblockbinary[i_40] == b'\xfd'[0]:
                                                    v1_48 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                                    i_40 += 3
                                                else:
                                                    v1_48 = rawblockbinary[i_40]
                                                    i_40 += 1
                                                i_40 += v1_48 #vout script
                                                j_44 += 1
                                            if coinbtx:
                                                blockminerreward = (str(v3_44//100000000)+'.'+str(v3_44%100000000//10000000)+str(v3_44%10000000//1000000)+str(v3_44%1000000//100000)+str(v3_44%100000//10000)+str(v3_44%10000//1000)+str(v3_44%1000//100)+str(v3_44%100//10)+str(v3_44%10)).encode()
                                                blockminerrewardstatus = b'ok'
                                            i_40 += 4 #locktime
                                            j += 1
                                        blockcoinbaserawlen = len(blockcoinbaseraw)
                                        j_40 = 0
                                        while j_40 < blockcoinbaserawlen:
                                            if blockcoinbaseraw[j_40] == b'"'[0]:
                                                blockcoinbase += b'&quot;'
                                            elif blockcoinbaseraw[j_40] == b'&'[0]:
                                                blockcoinbase += b'&amp;'
                                            elif blockcoinbaseraw[j_40] == b"'"[0]:
                                                blockcoinbase += b'&apos;'
                                            elif blockcoinbaseraw[j_40] == b'<'[0]:
                                                blockcoinbase += b'&lt;'
                                            elif blockcoinbaseraw[j_40] == b'>'[0]:
                                                blockcoinbase += b'&gt;'
                                            elif b' '[0] <= blockcoinbaseraw[j_40] and blockcoinbaseraw[j_40] <= b'~'[0]:
                                                blockcoinbase += blockcoinbaseraw[j_40:j_40+1]
                                            else:
                                                blockcoinbase += b'\\x' + blockcoinbaseraw[j_40:j_40+1].hex().encode()
                                            j_40 += 1
                                        blockcoinbasestatus = b'ok'
                                    except IndexError:
                                        blocktxcountstatus = b'invalid raw block received'
                                        blockminerrewardstatus = b'invalid raw block received'
                                        blockcoinbasestatus = b'invalid raw block received'
                                blocktimestatus = b'not processed'
                                blocktime = b''
                                if rawblockbinary == None:
                                    try:
                                        blocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(datajsonobject['result']['time'])).encode()
                                        blocktimestatus = b'ok'
                                    except KeyError:
                                        blocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocktimestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocktimestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    i_36 = 4 #block version
                                    i_36 += 32 #previous block hash
                                    i_36 += 32 #merkle root
                                    try:
                                        blocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(rawblockbinary[i_36] + rawblockbinary[i_36+1]*(1<<8) + rawblockbinary[i_36+2]*(1<<16) + rawblockbinary[i_36+3]*(1<<24))).encode()
                                        blocktimestatus = b'ok'
                                    except IndexError:
                                        blocktimestatus += b'invalid raw block received'
                                blockmediantimestatus = b'not processed'
                                blockmediantime = b''
                                try:
                                    blockmediantime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(datajsonobject['result']['mediantime'])).encode()
                                    blockmediantimestatus = b'ok'
                                except KeyError:
                                    blockmediantimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockmediantimestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockmediantimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockmediantimestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                blocknoncestatus = b'not processed'
                                blocknonce = b''
                                if rawblockbinary == None:
                                    try:
                                        blocknonce = hex(datajsonobject['result']['nonce']).encode()
                                        blocknoncestatus = b'ok'
                                    except KeyError:
                                        blocknoncestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocknoncestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blocknoncestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blocknoncestatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    i_36 = 4 #block version
                                    i_36 += 32 #previous block hash
                                    i_36 += 32 #merkle root
                                    i_36 += 4 #time
                                    i_36 += 4 #bits
                                    try:
                                        blocknonce = hex(rawblockbinary[i_36] + rawblockbinary[i_36+1]*(1<<8) + rawblockbinary[i_36+2]*(1<<16) + rawblockbinary[i_36+3]*(1<<24)).encode()
                                        blocknoncestatus = b'ok'
                                    except IndexError:
                                        blocknoncestatus = b'invalid raw block received'
                                blockbitsstatus = b'not processed'
                                blockbits = b''
                                if rawblockbinary == None:
                                    try:
                                        blockbits = datajsonobject['result']['bits'].encode()
                                        blockbitsstatus = b'ok'
                                    except KeyError:
                                        blockbitsstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockbitsstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blockbitsstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockbitsstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    i_36 = 4 #block version
                                    i_36 += 32 #previous block hash
                                    i_36 += 32 #merkle root
                                    i_36 += 4 #time
                                    try:
                                        blockbits = rawblockhex[(i_36+3)*2:(i_36+4)*2] + rawblockhex[(i_36+2)*2:(i_36+3)*2] + rawblockhex[(i_36+1)*2:(i_36+2)*2] + rawblockhex[(i_36)*2:(i_36+1)*2]
                                        blockbitsstatus = b'ok'
                                    except IndexError:
                                        blockbitsstatus = b'invalid raw block received'
                                blockdifficultystatus = b'not processed'
                                blockdifficulty = b''
                                try:
                                    blockdifficulty = str(datajsonobject['result']['difficulty']).encode()
                                    blockdifficultystatus = b'ok'
                                except KeyError:
                                    blockdifficultystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockdifficultystatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockdifficultystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockdifficultystatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                blockchainworkstatus = b'not processed'
                                blockchainwork = b''
                                try:
                                    blockchainwork = datajsonobject['result']['chainwork'].encode()
                                    blockchainworkstatus = b'ok'
                                except KeyError:
                                    blockchainworkstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockchainworkstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blockchainworkstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blockchainworkstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                blockpreviousblockhashstatus = b'not processed'
                                blockpreviousblockhash = b''
                                if rawblockbinary == None:
                                    try:
                                        blockpreviousblockhash = datajsonobject['result']['previousblockhash'].encode()
                                        blockpreviousblockhashstatus = b'ok'
                                    except KeyError:
                                        blockpreviousblockhashstatus = b'no previous block hash'
                                        try:
                                            blockpreviousblockhashstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        blockpreviousblockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            blockpreviousblockhashstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                        except TypeError:
                                            pass
                                else:
                                    i_36 = 4 #block version
                                    try:
                                        v1_40 = rawblockbinary[i_36:i_36+32]
                                        if v1_40 == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                                            blockpreviousblockhashstatus = b'no previous block hash'
                                        else:
                                            i_44 = 0
                                            v1_40len = len(v1_40) # = 32
                                            while i_44 < v1_40len:
                                                blockpreviousblockhash += v1_40[v1_40len - 1 - i_44:v1_40len - i_44].hex().encode()
                                                i_44 += 1
                                            blockpreviousblockhashstatus = b'ok'
                                    except IndexError:
                                        blockbitsstatus = b'invalid raw block received'
                                blocknextblockhashstatus = b'not processed'
                                blocknextblockhash = b''
                                try:
                                    blocknextblockhash = datajsonobject['result']['nextblockhash'].encode()
                                    blocknextblockhashstatus = b'ok'
                                except KeyError:
                                    blocknextblockhashstatus = b'no next block hash'
                                    try:
                                        blocknextblockhashstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                except TypeError:
                                    blocknextblockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        blocknextblockhashstatus = b'rpc json error message: ' + datajsonobject['error']['message'].encode()
                                    except TypeError:
                                        pass
                                responsepart3 = b''
                                responsepart3 += b' <b>Hash</b>: <a href="/getblockbyhash/' + blockhash + b'/">' + blockhash + b'</a> <br/>'
                                if blockrawheaderstatus == b'ok':
                                    responsepart3 += b' <b>Raw Header</b>: ' + blockrawheader + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Raw Header</b>: <span style="color:red;">' + blockrawheaderstatus + b'</span> <br/>'
                                if blockconfirmationsstatus == b'ok':
                                    responsepart3 += b' <b>Confirmations</b>: ' + blockconfirmations + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Confirmations</b>: <span style="color:red;">' + blockconfirmationsstatus + b'</span> <br/>'
                                if blocksizestatus == b'ok':
                                    responsepart3 += b' <b>Size</b>: ' + blocksize + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Size</b>: <span style="color:red;">' + blocksizestatus + b'</span> <br/>'
                                if blockheightstatus == b'ok':
                                    responsepart3 += b' <b>Height</b>: <a href="/getblockbyheight/' + blockheight + b'/">' + blockheight + b'</a> <br/>'
                                else:
                                    responsepart3 += b' <b>Height</b>: <span style="color:red;">' + blockheightstatus + b'</span> <br/>'
                                if blockversionstatus == b'ok':
                                    responsepart3 += b' <b>Version</b>: ' + blockversion + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Version</b>: <span style="color:red;">' + blockversionstatus + b'</span> <br/>'
                                if blockmerklerootstatus == b'ok':
                                    responsepart3 += b' <b>Merkle Root</b>: ' + blockmerkleroot + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Merkle Root</b>: <span style="color:red;">' + blockmerklerootstatus + b'</span> <br/>'
                                col72len = len(blocktxarray)
                                col72_i = 0
                                alltxlinkpart = b''
                                while col72_i < col72len:
                                    col76txid = b''
                                    col72txidstatus = b'not processed'
                                    try:
                                        col76txid, col80_x = blocktxarray[col72_i]
                                        col72txidstatus = b'ok'
                                    except ValueError:
                                        col76txid, = blocktxarray[col72_i]
                                        col72txidstatus = b'ok'
                                    if col72txidstatus == b'ok':
                                        alltxlinkpart += b'/tx/' + col76txid
                                    col72_i += 1
                                if blocktxcountstatus == b'ok':
                                    responsepart3 += b' <b>Transaction Count</b>: ' + blocktxcount + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Transaction Count</b>: <span style="color:red;">' + blocktxcountstatus + b'</span> <br/>'
                                if alltxlinkpart != b'':
                                    responsepart3 += b' Show all transactions in this block <a href="/getblockbyhash/' + blockhash + alltxlinkpart + b'/">' + b'with block headers</a>, <a href="' + alltxlinkpart + b'/">separately</a> <br/>'
                                if blockminerrewardstatus == b'ok':
                                    responsepart3 += b' <b>Miner Reward</b>: ' + blockminerreward + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Miner Reward</b>: <span style="color:red;">' + blockminerrewardstatus + b'</span> <br/>'
                                if blockcoinbasestatus == b'ok':
                                    responsepart3 += b' <b>Coinbase</b>: ' + blockcoinbase + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Coinbase</b>: <span style="color:red;">' + blockcoinbasestatus + b'</span> <br/>'
                                if blocktimestatus == b'ok':
                                    responsepart3 += b' <b>Time</b>: ' + blocktime + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Time</b>: <span style="color:red;">' + blocktimestatus + b'</span> <br/>'
                                if blockmediantimestatus == b'ok':
                                    responsepart3 += b' <b>Median Time</b>: ' + blockmediantime + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Median Time</b>: <span style="color:red;">' + blockmediantimestatus + b'</span> <br/>'
                                if blocknoncestatus == b'ok':
                                    responsepart3 += b' <b>Nonce</b>: ' + blocknonce + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Nonce</b>: <span style="color:red;">' + blocknoncestatus + b'</span> <br/>'
                                if blockbitsstatus == b'ok':
                                    responsepart3 += b' <b>Bits</b>: ' + blockbits + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Bits</b>: <span style="color:red;">' + blockbitsstatus + b'</span> <br/>'
                                if blockdifficultystatus == b'ok':
                                    responsepart3 += b' <b>Difficulty</b>: ' + blockdifficulty + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Difficulty</b>: <span style="color:red;">' + blockdifficultystatus + b'</span> <br/>'
                                if blockchainworkstatus == b'ok':
                                    responsepart3 += b' <b>Chain Work</b>: ' + blockchainwork + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Chain Work</b>: <span style="color:red;">' + blockchainworkstatus + b'</span> <br/>'
                                if blockpreviousblockhashstatus == b'ok':
                                    responsepart3 += b' <b>Previous Block Hash</b>: <a href="/getblockbyhash/' + blockpreviousblockhash + b'/">' + blockpreviousblockhash + b'</a> <br/>'
                                else:
                                    responsepart3 += b' <b>Previous Block Hash</b>: <span style="color:red;">' + blockpreviousblockhashstatus + b'</span> <br/>'
                                if blocknextblockhashstatus == b'ok':
                                    responsepart3 += b' <b>Next Block Hash</b>: <a href="/getblockbyhash/' + blocknextblockhash + b'/">' + blocknextblockhash + b'</a> <br/>'
                                else:
                                    responsepart3 += b' <b>Next Block Hash</b>: <span style="color:red;">' + blocknextblockhashstatus + b'</span> <br/>'
                                responsepart2 += responsepart3
                            except json.decoder.JSONDecodeError:
                                blockhashquerystatus = b'could not interpret rpc json response, data = ' + data.__repr__().encode()
                            except AttributeError:
                                blockhashquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                        else:
                           blockhashquerystatus = b'rpc response delivery status: ' + rpcstatus
                    else:
                        blockhashquerystatus = blockhashstatus
                    if blockhashquerystatus != b'no errors':
                        responsepart2 += b' <b>Error while processing requested block: <span style="color:red;">' + blockhashquerystatus + b'</span></b> <br/>'
                if httpchoice == b'address':
                    addressquerystatus = b'no errors'
                    addresstransactioncountfor = b''
                    if addressstatus == b'ok':
                        addressqueryhandle = queue.Queue()
                        searchrawtransactionsparamskip = 0
                        searchrawtransactionsparamcount = 2147483647
                        addresstxarray = []
                        while addressquerystatus == b'no errors':
                            requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "searchrawtransactions", "params": ["' + address + b'", 1, ' + str(searchrawtransactionsparamskip).encode() + b', ' + str(searchrawtransactionsparamcount).encode() + b'], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', addressqueryhandle))
                            livelastactivity[0] = time.time()
                            addressrpcstatus, addressrpcdata = addressqueryhandle.get()
                            livelastactivity[0] = time.time()
                            if addressrpcstatus == b'received':
                                try:
                                    addressrpcjsondata = json.loads(addressrpcdata.decode())
                                    responsetxcount = len(addressrpcjsondata['result'])
                                    j = 0
                                    while j < responsetxcount:
                                        txisrequested = False
                                        foundtxid = addressrpcjsondata['result'][j]['txid'].encode()
                                        searchrawtransactionsparamskip += 1
                                        try:
                                            x = requestedtxarray[requestedtxmap[foundtxid]]
                                            txisrequested = True
                                        except KeyError:
                                            pass
                                        if txisrequested:
                                            addresstxarray += [(foundtxid, queue.Queue())]
                                        else:
                                            addresstxarray += [(foundtxid,)]
                                        j += 1
                                    if responsetxcount < searchrawtransactionsparamcount:
                                        break
                                    searchrawtransactionsparamcount = searchrawtransactionsparamcount * searchrawtransactionsparamcount + 1
                                    if searchrawtransactionsparamcount > 2147483647:
                                        searchrawtransactionsparamcount = 2147483647
                                except json.decoder.JSONDecodeError:
                                    addressquerystatus = b'could not interpret rpc json response, addressrpcdata = ' + addressrpcdata.__repr__().encode()
                                except TypeError:
                                    try:
                                        col80errmsg = addressrpcjsondata['error']['message'].encode()
                                        if col80errmsg == b'Cannot read transaction from disk':
                                            if searchrawtransactionsparamcount == 1:
                                                searchrawtransactionsparamskip += 1
                                            elif searchrawtransactionsparamcount >= 1000:
                                                searchrawtransactionsparamcount = 32
                                            elif searchrawtransactionsparamcount >= 32:
                                                searchrawtransactionsparamcount = 6
                                            elif searchrawtransactionsparamcount >= 6:
                                                searchrawtransactionsparamcount = 2
                                            elif searchrawtransactionsparamcount >= 2:
                                                searchrawtransactionsparamcount = 1
                                        else:
                                            addressquerystatus = b'rpc json error message: ' + col80errmsg
                                    except KeyError:
                                        addressquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    except AttributeError:
                                        addressquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                except KeyError:
                                    addressquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        addressquerystatus = b'rpc json error message: ' + addressrpcjsondata['error']['message'].encode()
                                    except TypeError:
                                        pass
                            else:
                                addressquerystatus = b'rpc response delivery status: ' + addressrpcstatus
                        addresstransactioncountfor = str(len(addresstxarray)).encode()
                        returnedtxlist = addresstxarray[:]
                    else:
                        addressquerystatus = addressstatus
                    if addressquerystatus == b'no errors':
                        col64len = len(returnedtxlist)
                        col64_i = 0
                        alltxlinkpart = b''
                        while col64_i < col64len:
                            col68txid = b''
                            col68txidstatus = b'not processed'
                            try:
                                col68txid, col72_x = returnedtxlist[col64_i]
                                col68txidstatus = b'ok'
                            except ValueError:
                                col68txid, = returnedtxlist[col64_i]
                                col68txidstatus = b'ok'
                            if col68txidstatus == b'ok':
                                alltxlinkpart += b'/tx/' + col68txid
                            col64_i += 1
                        responsepart2 += b' <b>Transaction Count For Address ' + address + b'</b>: ' + addresstransactioncountfor + b' <br/>'
                        if alltxlinkpart != b'':
                            responsepart2 += b' Show all transactions for this address <a href="/address/' + address + alltxlinkpart + b'/">' + b'with address info</a>, <a href="' + alltxlinkpart + b'/">separately</a> <br/>'
                    else:
                        responsepart2 += b' <b>Error while processing requested address: <span style="color:red;">' + addressquerystatus + b'</span></b> <br/>'
                if httpchoice == b'mempool':
                    mempoolquerystatus = b'no errors'
                    mempoolqueryhandle = queue.Queue()
                    mempooltransactioncount = b''
                    mempooltransactioncountinteger = 0
                    mempooltransactioncountstatus = b'not processed'
                    requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawmempool", "params": [false], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', mempoolqueryhandle))
                    livelastactivity[0] = time.time()
                    mempoolrpcstatus, mempoolrpcdata = mempoolqueryhandle.get()
                    livelastactivity[0] = time.time()
                    mempooltxarray = []
                    if mempoolrpcstatus == b'received':
                        try:
                            mempoolrpcjsondata = json.loads(mempoolrpcdata.decode())
                            mempooltransactioncountinteger = len(mempoolrpcjsondata['result'])
                            mempooltransactioncount = str(mempooltransactioncountinteger).encode()
                            mempooltransactioncountstatus = b'ok'
                            j = 0
                            while j < mempooltransactioncountinteger:
                                foundtxid = mempoolrpcjsondata['result'][j].encode()
                                txisrequested = False
                                try:
                                    x = requestedtxarray[requestedtxmap[foundtxid]]
                                    txisrequested = True
                                except KeyError:
                                    pass
                                if txisrequested:
                                    mempooltxarray += [(foundtxid, queue.Queue())]
                                else:
                                    mempooltxarray += [(foundtxid,)]
                                j += 1
                        except json.decoder.JSONDecodeError:
                            mempoolquerystatus = b'could not interpret rpc json response, mempoolrpcdata = ' + mempoolrpcdata.__repr__().encode()
                        except TypeError:
                            mempoolquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                        except KeyError:
                            mempoolquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                        except AttributeError:
                            mempoolquerystatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                    else:
                        mempoolquerystatus = b'rpc response delivery status: ' + mempoolrpcstatus
                    if mempoolquerystatus == b'no errors':
                        mempooltransactioncountinteger = len(mempooltxarray)
                        col64_i = 0
                        alltxlinkpart = b''
                        while col64_i < mempooltransactioncountinteger:
                            col68txid = b''
                            col68txidstatus = b'not processed'
                            try:
                                col68txid, col72_x = mempooltxarray[col64_i]
                                col68txidstatus = b'ok'
                            except ValueError:
                                col68txid, = mempooltxarray[col64_i]
                                col68txidstatus = b'ok'
                            if col68txidstatus == b'ok':
                                alltxlinkpart += b'/tx/' + col68txid
                            col64_i += 1
                        responsepart2 += b' <b>Transaction Count</b>: ' + mempooltransactioncount + b' <br/>'
                        if alltxlinkpart != b'':
                            responsepart2 += b' Show all transactions in mempool <a href="/mempool' + alltxlinkpart + b'/">' + b'with mempool info</a>, <a href="' + alltxlinkpart + b'/">separately</a> <br/>'
                    else:
                        responsepart2 += b' <b>Error while accessing mempool: <span style="color:red;">' + mempoolquerystatus + b'</span></b> <br/>'
                    returnedtxlist = mempooltxarray[:]
                # Start processing requested transactions
                if httpchoice != b'block' and httpchoice != b'address' and httpchoice != b'mempool':
                    returnedtxlist = []
                    for requestedtxindex, requestedtxid in enumerate(requestedtxarray):
                        try:
                            if requestedtxmap[requestedtxid] == requestedtxindex:
                                returnedtxlist += [(requestedtxid, queue.Queue())]
                        except KeyError:
                            pass
                j = 0
                returnedtxcount = len(returnedtxlist)
                while j < returnedtxcount:
                    try:
                        col64txid, col64queue = returnedtxlist[j]
                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + col64txid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', col64queue))
                        livelastactivity[0] = time.time()
                    except ValueError:
                        pass
                    j += 1
                j = 0
                txresponsemap = {}
                txsizefeepairs = []
                txfeesumintegersatoshis = 0
                txfeesumintegerstatus = b'no errors'
                responsepart2_5 = b''
                try:
                    if httpchoice == b'block' and rawblockbinary != None:
                        rawblockindex = 80
                        if rawblockbinary[rawblockindex] == b'\xff'[0]:
                            rawblockindex += 9
                        elif rawblockbinary[rawblockindex] == b'\xfe'[0]:
                            rawblockindex += 5
                        elif rawblockbinary[rawblockindex] == b'\xfd'[0]:
                            rawblockindex += 3
                        else:
                            rawblockindex += 1
                except IndexError:
                    rawblockbinary = None
                while j < returnedtxcount:
                    responsepart3 = b''
                    rawtxhexhint = b''
                    rawtxhint = b''
                    try:
                        if httpchoice == b'block' and rawblockbinary != None:
                            i_28 = rawblockindex
                            i_28 += 4 #transaction version
                            v1_28 = 0 #transaction vin count
                            if rawblockbinary[i_28] == b'\xff'[0]:
                                v1_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24) + rawblockbinary[i_28+5]*(1<<32) + rawblockbinary[i_28+6]*(1<<40) + rawblockbinary[i_28+7]*(1<<48) + rawblockbinary[i_28+8]*(1<<56)
                                i_28 += 9
                            elif rawblockbinary[i_28] == b'\xfe'[0]:
                                v1_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24)
                                i_28 += 5
                            elif rawblockbinary[i_28] == b'\xfd'[0]:
                                v1_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8)
                                i_28 += 3
                            else:
                                v1_28 = rawblockbinary[i_28]
                                i_28 += 1
                            j_28 = 0
                            while j_28 < v1_28:
                                i_28 += 32 #vin previous txid
                                i_28 += 4 #vin previous txid index
                                v1_32 = 0 #vin script len
                                if rawblockbinary[i_28] == b'\xff'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24) + rawblockbinary[i_28+5]*(1<<32) + rawblockbinary[i_28+6]*(1<<40) + rawblockbinary[i_28+7]*(1<<48) + rawblockbinary[i_28+8]*(1<<56)
                                    i_28 += 9
                                elif rawblockbinary[i_28] == b'\xfe'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24)
                                    i_28 += 5
                                elif rawblockbinary[i_28] == b'\xfd'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8)
                                    i_28 += 3
                                else:
                                    v1_32 = rawblockbinary[i_28]
                                    i_28 += 1
                                i_28 += v1_32 #vin script sometimes coinbase
                                i_28 += 4 #vin sequenceno
                                j_28 += 1
                            v2_28 = 0 #transaction vout count
                            if rawblockbinary[i_28] == b'\xff'[0]:
                                v2_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24) + rawblockbinary[i_28+5]*(1<<32) + rawblockbinary[i_28+6]*(1<<40) + rawblockbinary[i_28+7]*(1<<48) + rawblockbinary[i_28+8]*(1<<56)
                                i_28 += 9
                            elif rawblockbinary[i_28] == b'\xfe'[0]:
                                v2_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24)
                                i_28 += 5
                            elif rawblockbinary[i_28] == b'\xfd'[0]:
                                v2_28 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8)
                                i_28 += 3
                            else:
                                v2_28 = rawblockbinary[i_28]
                                i_28 += 1
                            j_28 = 0
                            while j_28 < v2_28:
                                i_28 += 8 #vout value
                                v1_32 = 0 #vout script len
                                if rawblockbinary[i_28] == b'\xff'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24) + rawblockbinary[i_28+5]*(1<<32) + rawblockbinary[i_28+6]*(1<<40) + rawblockbinary[i_28+7]*(1<<48) + rawblockbinary[i_28+8]*(1<<56)
                                    i_28 += 9
                                elif rawblockbinary[i_28] == b'\xfe'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8) + rawblockbinary[i_28+3]*(1<<16) + rawblockbinary[i_28+4]*(1<<24)
                                    i_28 += 5
                                elif rawblockbinary[i_28] == b'\xfd'[0]:
                                    v1_32 = rawblockbinary[i_28+1] + rawblockbinary[i_28+2]*(1<<8)
                                    i_28 += 3
                                else:
                                    v1_32 = rawblockbinary[i_28]
                                    i_28 += 1
                                i_28 += v1_32 #vout script
                                j_28 += 1
                            i_28 += 4 #locktime
                            rawtxhexhint = rawblockhex[rawblockindex*2:i_28*2]
                            rawtxhint = rawblockbinary[rawblockindex:i_28]
                            rawblockindex = i_28
                    except IndexError:
                        rawblockbinary == None
                    try:
                        col24status = b'no errors'
                        col24txid, col24queue = returnedtxlist[j]
                        col24rpcstatus, col24rpcdata = col24queue.get()
                        livelastactivity[0] = time.time()
                        responsepart3 += b' <a href="/tx/' + col24txid + b'/">' + col24txid + b'</a> <br/>'
                        if col24rpcstatus == b'received':
                            try:
                                col32jsondata = json.loads(col24rpcdata.decode())
                                transactionsizeinteger = 0
                                transactionsizeintegerstatus = b'not processed'
                                transactionhex = b''
                                transactionbinary = b''
                                transactionhexstatus = b'not processed'
                                try:
                                    if col32jsondata['error']['message'].encode() == b'No information available about transaction' and rawtxhexhint:
                                        col40queue = queue.Queue()
                                        requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "decoderawtransaction", "params": ["' + rawtxhexhint + b'"], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', col40queue))
                                        livelastactivity[0] = time.time()
                                        col24rpcstatus, col24rpcdata = col40queue.get()
                                        livelastactivity[0] = time.time()
                                        if col24rpcstatus == b'received':
                                            col32jsondata = json.loads(col24rpcdata.decode())
                                            if col32jsondata['result']['txid'].encode() == col24txid:
                                                col32jsondata['result']['hex'] = rawtxhexhint.decode()
                                                col24rpcdata = json.dumps(col32jsondata).encode() + b'\n'
                                            if col32jsondata['result']['txid'].encode() != col24txid:
                                                rawtxhexhint = None
                                                rawtxhint = None
                                        else:
                                            col24status = b'rpc response delivery status: ' + col24rpcstatus
                                except TypeError:
                                    pass
                                if rawtxhint:
                                    transactionhex = rawtxhexhint
                                    transactionbinary = rawtxhint
                                    transactionhexstatus = b'ok'
                                else:
                                    transactionbinary = b''
                                    try:
                                        transactionhex = col32jsondata['result']['hex'].encode()
                                        transactionhexstatus = b'ok'
                                    except KeyError:
                                        transactionhexstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionhexstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        transactionhexstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionhexstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    if transactionhexstatus == b'ok':
                                        try:
                                            transactionbinary = bytes.fromhex(transactionhex.decode())
                                        except ValueError:
                                            pass
                                        if len(transactionbinary) != (len(transactionhex)>>1) or (not transactionhex):
                                            transactionbinary = None
                                transactiontxid = col24txid
                                txresponsemap[transactiontxid] = (col24rpcstatus, col24rpcdata, None)
                                transactiontxidstatus = b'ok'
                                transactionsize = b''
                                transactionsizestatus = b'not processed'
                                if transactionbinary:
                                    try:
                                        transactionsizeinteger = len(transactionbinary)
                                        transactionsizeintegerstatus = b'ok'
                                        transactionsize = str(len(transactionbinary)).encode()
                                        transactionsizestatus = b'ok'
                                    except IndexError:
                                        transactionsizestatus = b'invalid raw tx received'
                                else:
                                    try:
                                        transactionsizeinteger = col32jsondata['result']['size']
                                        transactionsizeintegerstatus = b'ok'
                                        transactionsize = str(transactionsizeinteger).encode()
                                        transactionsizestatus = b'ok'
                                    except TypeError:
                                        transactionsizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionsizestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except KeyError:
                                        transactionsizestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionsizestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                transactionpositioninblock = b''
                                transactionpositioninblockstatus = b'not processed'
                                if httpchoice == b'block' and rawtxhint:
                                    transactionpositioninblock = str(rawblockindex-len(rawtxhint)).encode()
                                    transactionpositioninblockstatus = b'ok'
                                transactionversion = b''
                                transactionversionstatus = b'not processed'
                                if transactionbinary:
                                    try:
                                        transactionversion = hex(transactionbinary[0]+transactionbinary[1]*(1<<8)+transactionbinary[2]*(1<<16)+transactionbinary[3]*(1<<24)).encode()
                                        transactionversionstatus = b'ok'
                                    except IndexError:
                                        transactionversionstatus = b'invalid raw tx received'
                                else:
                                    try:
                                        transactionversion = hex(col32jsondata['result']['version']).encode()
                                        transactionversionstatus = b'ok' + hex(col32jsondata['result']['version']).encode()
                                    except TypeError:
                                        transactionversionstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionversionstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except KeyError:
                                        transactionversionstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionversionstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                transactionlocktime = b''
                                transactionlocktimestatus = b'not processed'
                                if transactionbinary:
                                    try:
                                        v1_40 = len(transactionbinary) - 4
                                        v2_40 = transactionbinary[v1_40] + transactionbinary[v1_40+1]*(1<<8) + transactionbinary[v1_40+2]*(1<<16) + transactionbinary[v1_40+3]*(1<<24)
                                        if v2_40 == (1<<32)-1:
                                            transactionlocktime = hex(v2_40).encode()
                                        elif v2_40 >= 500000000:
                                            transactionlocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(v2_40)).encode()
                                        else:
                                            transactionlocktime = str(v2_40).encode()
                                        transactionlocktimestatus = b'ok'
                                    except IndexError:
                                        transactionlocktimestatus = b'invalid raw tx received'
                                else:
                                    try:
                                        v2_40 = col32jsondata['result']['locktime']
                                        if v2_40 == (1<<32)-1:
                                            transactionlocktime = hex(v2_40).encode()
                                        elif v2_40 >= 500000000:
                                            transactionlocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(v2_40)).encode()
                                        else:
                                            transactionlocktime = str(v2_40).encode()
                                        transactionlocktimestatus = b'ok'
                                    except KeyError:
                                        transactionlocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionlocktimestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        transactionlocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionlocktimestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                transactionvincountinteger = 0
                                transactionvincountstatus = b'not processed'
                                transactionvincount = b''
                                transactionvoutcountinteger = 0
                                transactionvoutcountstatus = b'not processed'
                                transactionvoutcount = b''
                                if transactionbinary:
                                    try:
                                        i_40 = 4 #transaction version
                                        v1_40 = 0 #transaction vin count
                                        if rawblockbinary[i_40] == b'\xff'[0]:
                                            v1_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                            i_40 += 9
                                        elif rawblockbinary[i_40] == b'\xfe'[0]:
                                            v1_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                            i_40 += 5
                                        elif rawblockbinary[i_40] == b'\xfd'[0]:
                                            v1_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                            i_40 += 3
                                        else:
                                            v1_40 = rawblockbinary[i_40]
                                            i_40 += 1
                                        transactionvincountinteger = v1_40
                                        transactionvincount = str(transactionvincountinteger).encode()
                                        transactionvincountstatus = b'ok'
                                        j_40 = 0
                                        while j_40 < v1_40:
                                            col44txid = b''
                                            i_44 = 0
                                            while i_44 < 32:
                                                col44txid += transactionbinary[i_40 + 31 - i_44:i_40 + 32 - i_44].hex().encode()
                                                i_44 += 1
                                            i_40 += 32 #vin previous txid
                                            v1_44 = transactionbinary[i_40] + transactionbinary[i_40+1]*(1<<8) + transactionbinary[i_40+2]*(1<<16) + transactionbinary[i_40+3]*(1<<24)
                                            i_40 += 4 #vin previous txid index
                                            v2_44 = 0 #vin script len
                                            if transactionbinary[i_40] == b'\xff'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24) + transactionbinary[i_40+5]*(1<<32) + transactionbinary[i_40+6]*(1<<40) + transactionbinary[i_40+7]*(1<<48) + transactionbinary[i_40+8]*(1<<56)
                                                i_40 += 9
                                            elif transactionbinary[i_40] == b'\xfe'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24)
                                                i_40 += 5
                                            elif transactionbinary[i_40] == b'\xfd'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8)
                                                i_40 += 3
                                            else:
                                                v2_44 = transactionbinary[i_40]
                                                i_40 += 1
                                            i_40 += v2_44 #vin script sometimes coinbase
                                            i_40 += 4 #vin sequenceno
                                            j_40 += 1
                                            if not (col44txid == b'0000000000000000000000000000000000000000000000000000000000000000' and v1_44 == (1<<32)-1):
                                                try:
                                                    col48_x = txresponsemap[col44txid]
                                                except KeyError:
                                                    col48queue = queue.Queue()
                                                    requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + col44txid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', col48queue))
                                                    livelastactivity[0] = time.time()
                                                    txresponsemap[col44txid] = (None, None, col48queue)
                                        v2_40 = 0 #transaction vout count
                                        if rawblockbinary[i_40] == b'\xff'[0]:
                                            v2_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24) + rawblockbinary[i_40+5]*(1<<32) + rawblockbinary[i_40+6]*(1<<40) + rawblockbinary[i_40+7]*(1<<48) + rawblockbinary[i_40+8]*(1<<56)
                                            i_40 += 9
                                        elif rawblockbinary[i_40] == b'\xfe'[0]:
                                            v2_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8) + rawblockbinary[i_40+3]*(1<<16) + rawblockbinary[i_40+4]*(1<<24)
                                            i_40 += 5
                                        elif rawblockbinary[i_40] == b'\xfd'[0]:
                                            v2_40 = rawblockbinary[i_40+1] + rawblockbinary[i_40+2]*(1<<8)
                                            i_40 += 3
                                        else:
                                            v2_40 = rawblockbinary[i_40]
                                            i_40 += 1
                                        transactionvoutcountinteger = v1_40
                                        transactionvoutcount = str(transactionvoutcountinteger).encode()
                                        transactionvoutcountstatus = b'ok'
                                    except IndexError:
                                        transactionvincountstatus = b'invalid raw tx received'
                                        transactionvoutcountstatus = b'invalid raw tx received'
                                else:
                                    try:
                                        transactionvincountinteger = len(col32jsondata['result']['vin'])
                                        transactionvincount = str(transactionvincountinteger).encode()
                                        transactionvincountstatus = b'ok'
                                        col40_i = 0
                                        while col40_i < transactionvincountinteger:
                                            try:
                                                col48txid = col32jsondata['result']['vin'][col40_i]['txid'].encode()
                                                try:
                                                    col52_x = txresponsemap[col48txid]
                                                except KeyError:
                                                    col52queue = queue.Queue()
                                                    requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + col48txid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', col52queue))
                                                    livelastactivity[0] = time.time()
                                                    txresponsemap[col48txid] = (None, None, col52queue)
                                            except TypeError:
                                                pass
                                            except KeyError:
                                                pass
                                            col40_i += 1
                                    except KeyError:
                                        transactionvincountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionvincountstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        transactionvincountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionvincountstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    try:
                                        transactionvoutcountinteger = len(col32jsondata['result']['vout'])
                                        transactionvoutcount = str(transactionvoutcountinteger).encode()
                                        transactionvoutcountstatus = b'ok'
                                    except KeyError:
                                        transactionvoutcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionvoutcountstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                    except TypeError:
                                        transactionvoutcountstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                        try:
                                            transactionvoutcountstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                        except TypeError:
                                            pass
                                transactionblockhash = b''
                                transactionblockhashstatus = b'not processed'
                                try:
                                    transactionblockhash = col32jsondata['result']['blockhash'].encode()
                                    transactionblockhashstatus = b'ok'
                                except KeyError:
                                    transactionblockhashstatus = b'no block hash'
                                except TypeError:
                                    transactionblockhashstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactionblockhashstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                    except TypeError:
                                        pass
                                transactionconfirmations = b''
                                transactionconfirmationsstatus = b'not processed'
                                try:
                                    transactionconfirmations = str(col32jsondata['result']['confirmations']).encode()
                                    transactionconfirmationsstatus = b'ok'
                                except KeyError:
                                    transactionconfirmationsstatus = b'no confirmations'
                                except TypeError:
                                    transactionconfirmationsstatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactionconfirmationsstatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                    except TypeError:
                                        pass
                                transactiontime = b''
                                transactiontimestatus = b'not processed'
                                try:
                                    transactiontime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(col32jsondata['result']['time'])).encode()
                                    transactiontimestatus = b'ok'
                                except KeyError:
                                    transactiontimestatus = b'no time'
                                except TypeError:
                                    transactiontimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactiontimestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                    except TypeError:
                                        pass
                                transactionblocktime = b''
                                transactionblocktimestatus = b'not processed'
                                try:
                                    transactionblocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(col32jsondata['result']['blocktime'])).encode()
                                    transactionblocktimestatus = b'ok'
                                except KeyError:
                                    transactionblocktimestatus = b'no block time'
                                except TypeError:
                                    transactionblocktimestatus = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                    try:
                                        transactionblocktimestatus = b'rpc json error message: ' + col32jsondata['error']['message'].encode()
                                    except TypeError:
                                        pass
                                if transactionhexstatus == b'ok':
                                    responsepart3 += b' <b>Hex</b>: ' + transactionhex + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Hex</b>: <span style="color:red;">' + transactionhexstatus + b'</span> <br/>'
                                if transactiontxidstatus == b'ok':
                                    responsepart3 += b' <b>Tx Id</b>: <a href="/tx/' + transactiontxid + b'/">' + transactiontxid + b'</a> <br/>'
                                else:
                                    responsepart3 += b' <b>Tx Id</b>: <span style="color:red;">' + transactiontxidstatus + b'</span> <br/>'
                                if transactionsizestatus == b'ok':
                                    responsepart3 += b' <b>Size</b>: ' + transactionsize + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Size</b>: <span style="color:red;">' + transactionsizestatus + b'</span> <br/>'
                                if httpchoice == b'block':
                                    if transactionpositioninblockstatus == b'ok':
                                        responsepart3 += b' <b>Position in block</b>: ' + transactionpositioninblock + b' <br/>'
                                    else:
                                        responsepart3 += b' <b>Position in block</b>: <span style="color:red;">' + transactionpositioninblockstatus + b'</span> <br/>'
                                if transactionversionstatus == b'ok':
                                    responsepart3 += b' <b>Version</b>: ' + transactionversion + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Version</b>: <span style="color:red;">' + transactionversionstatus + b'</span> <br/>'
                                if transactionlocktimestatus == b'ok':
                                    responsepart3 += b' <b>Lock Time</b>: ' + transactionlocktime + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Lock Time</b>: <span style="color:red;">' + transactionlocktimestatus + b'</span> <br/>'
                                col72vinsumintegersatoshis = 0
                                col72vinsumintegerstatus = b'no errors'
                                col72isacoinbasetx = False
                                col72voutsumintegersatoshis = 0
                                col72voutsumintegerstatus = b'no errors'
                                if transactionbinary:
                                    try:
                                        i_40 = 4 #transaction version
                                        v1_40 = 0 #transaction vin count
                                        if transactionbinary[i_40] == b'\xff'[0]:
                                            v1_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24) + transactionbinary[i_40+5]*(1<<32) + transactionbinary[i_40+6]*(1<<40) + transactionbinary[i_40+7]*(1<<48) + transactionbinary[i_40+8]*(1<<56)
                                            i_40 += 9
                                        elif transactionbinary[i_40] == b'\xfe'[0]:
                                            v1_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24)
                                            i_40 += 5
                                        elif transactionbinary[i_40] == b'\xfd'[0]:
                                            v1_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8)
                                            i_40 += 3
                                        else:
                                            v1_40 = transactionbinary[i_40]
                                            i_40 += 1
                                        transactionvincountinteger = v1_40
                                        transactionvincount = str(transactionvincountinteger).encode()
                                        transactionvincountstatus = b'ok'
                                        responsepart3 += b' <b>Vin Count</b>: ' + transactionvincount + b' <br/>'
                                        j_40 = 0
                                        while j_40 < v1_40:
                                            responsepart4 = b''
                                            col44txid = b''
                                            i_44 = 0
                                            while i_44 < 32:
                                                col44txid += transactionbinary[i_40 + 31 - i_44:i_40 + 32 - i_44].hex().encode()
                                                i_44 += 1
                                            i_40 += 32 #vin previous txid
                                            col44voutinteger = transactionbinary[i_40] + transactionbinary[i_40+1]*(1<<8) + transactionbinary[i_40+2]*(1<<16) + transactionbinary[i_40+3]*(1<<24)
                                            col44vout = str(col44voutinteger).encode()
                                            i_40 += 4
                                            if not (col44txid == b'0000000000000000000000000000000000000000000000000000000000000000' and col44vout == str((1<<32)-1).encode()):
                                                try:
                                                    col48_x = txresponsemap[col44txid]
                                                except KeyError:
                                                    col48queue = queue.Queue()
                                                    requestrpcjobqueue.put((rpcsocketqueue, ipportpair, rpcauthpair, b'{"jsonrpc": "1.0", "method": "getrawtransaction", "params": ["' + col44txid + b'", 1], "id": "blockchainrpcserver_py_' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b'"}', col48queue))
                                                    livelastactivity[0] = time.time()
                                                    txresponsemap[col44txid] = (None, None, col48queue)
                                            v2_44 = 0 #vin script len
                                            if transactionbinary[i_40] == b'\xff'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24) + transactionbinary[i_40+5]*(1<<32) + transactionbinary[i_40+6]*(1<<40) + transactionbinary[i_40+7]*(1<<48) + transactionbinary[i_40+8]*(1<<56)
                                                i_40 += 9
                                            elif transactionbinary[i_40] == b'\xfe'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24)
                                                i_40 += 5
                                            elif transactionbinary[i_40] == b'\xfd'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8)
                                                i_40 += 3
                                            else:
                                                v2_44 = transactionbinary[i_40]
                                                i_40 += 1
                                            col44coinbase = b''
                                            col44scriptsigasm = b''
                                            if col44txid == b'0000000000000000000000000000000000000000000000000000000000000000' and col44vout == str((1<<32)-1).encode():
                                                col72isacoinbasetx = True
                                                i_48 = 0
                                                while i_48 < v2_44:
                                                    v1_52 = transactionbinary[i_40 + i_48:i_40 + i_48 + 1]
                                                    if v1_52 == b'"':
                                                        col44coinbase += b'&quot;'
                                                    elif v1_52 == b'&':
                                                        col44coinbase += b'&amp;'
                                                    elif v1_52 == b"'":
                                                        col44coinbase += b'&apos;'
                                                    elif v1_52 == b'<':
                                                        col44coinbase += b'&lt;'
                                                    elif v1_52 == b'>':
                                                        col44coinbase += b'&gt;'
                                                    elif b' ' <= v1_52 and v1_52 <= b'~':
                                                        col44coinbase += v1_52
                                                    else:
                                                        col44coinbase += b'\\x' + transactionbinary[i_40 + i_48:i_40 + i_48 + 1].hex().encode()
                                                    i_48 += 1
                                            else: #TODO: check scriptsig type decode samples other than 0x01-0x4b <sig> [0x01-0x4b <pubKey>]
                                                if 0 + 1 <= v2_44:
                                                    if 1 <= transactionbinary[i_40] and transactionbinary[i_40] <= 75 and transactionbinary[i_40] + 1 <= v2_44:
                                                        if transactionbinary[i_40+1+transactionbinary[i_40]-1] == 1:
                                                            col44scriptsigasm += transactionbinary[i_40+1:i_40+1+transactionbinary[i_40]-1].hex().encode() + b'[ALL] '
                                                        elif transactionbinary[i_40+1+transactionbinary[i_40]-1] == 2:
                                                            col44scriptsigasm += transactionbinary[i_40+1:i_40+1+transactionbinary[i_40]-1].hex().encode() + b'[NONE] '
                                                        elif transactionbinary[i_40+1+transactionbinary[i_40]-1] == 3:
                                                            col44scriptsigasm += transactionbinary[i_40+1:i_40+1+transactionbinary[i_40]-1].hex().encode() + b'[SINGLE] '
                                                        elif transactionbinary[i_40+1+transactionbinary[i_40]-1] == 128:
                                                            col44scriptsigasm += transactionbinary[i_40+1:i_40+1+transactionbinary[i_40]-1].hex().encode() + b'[ANYONECANPAY] '
                                                        else:
                                                            col44scriptsigasm += transactionbinary[i_40+1:i_40+1+transactionbinary[i_40]].hex().encode()
                                                        #print('col44scriptsigasm = ' + col44scriptsigasm.__repr__())
                                                        if transactionbinary[i_40] + 1 + 1 <= v2_44:
                                                            if transactionbinary[i_40] + 1 + transactionbinary[i_40+1+transactionbinary[i_40]] + 1 <= v2_44:
                                                                col44scriptsigasm += transactionbinary[i_40+1+transactionbinary[i_40]+1:i_40+transactionbinary[i_40] + 1 + transactionbinary[i_40+1+transactionbinary[i_40]] + 1].hex().encode()
                                                                #print('col44scriptsigasm = ' + col44scriptsigasm.__repr__())
                                                                if transactionbinary[i_40] + 1 + transactionbinary[i_40+1+transactionbinary[i_40]] + 1 < v2_44:
                                                                    col44scriptsigasm += b' ?' + transactionbinary[i_40+transactionbinary[i_40] + 1 + transactionbinary[i_40+1+transactionbinary[i_40]] + 1:i_40+v2_44].hex().encode()
                                                            else:
                                                                col44scriptsigasm += b' ?' + transactionbinary[i_40+1+transactionbinary[i_40]::i_40+v2_44].hex().encode()
##                                                        else:
##                                                            print('transactionbinary[i_40] + 1 + 1 <= v2_44 === ' + (transactionbinary[i_40] + 1 + 1).__repr__() + ' <= ' + v2_44.__repr__())
                                                    else:
                                                        col44scriptsigasm = b'?' + transactionbinary[i_40:i_40+v2_44].hex().encode()
                                                else:
                                                    col44scriptsigasm = b'&lt;void&gt;'
                                                #print('col44scriptsigasm = ' + col44scriptsigasm.__repr__())
                                            i_40 += v2_44 #vin script sometimes coinbase
                                            col44sequence = hex(transactionbinary[i_40] + transactionbinary[i_40+1]*(1<<8) + transactionbinary[i_40+2]*(1<<16) + transactionbinary[i_40+3]*(1<<24)).encode()
                                            i_40 += 4 #vin sequenceno
                                            col44valueintegersatoshis = 0
                                            col44value = b''
                                            col44valuestatus = b'not processed'
                                            col44addresslist = None
                                            if not (col44txid == b'0000000000000000000000000000000000000000000000000000000000000000' and col44vout == str((1<<32)-1).encode()):
                                                try:
                                                    col48status, col48data, col48queue = txresponsemap[col44txid]
                                                    if col48queue:
                                                        col48status, col48data = col48queue.get()
                                                        col48queue = None
                                                        txresponsemap[col44txid] = col48status, col48data, col48queue
                                                    if col48status == b'received':
                                                        col52transactionbinary = b''
                                                        try:
                                                            v1_56 = json.loads(col48data.decode())
                                                            col52transactionbinary = bytes.fromhex(json.loads(col48data.decode())['result']['hex'])
                                                        except TypeError:
                                                            print('no hex for ' + col44txid.__repr__() + ' (found at ' + transactiontxid.__repr__() + ')? col48data = ' + col48data.__repr__())
                                                        i_52 = 4 #transaction version
                                                        v1_52 = 0 #transaction vin count
                                                        if col52transactionbinary[i_52] == b'\xff'[0]:
                                                            v1_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24) + col52transactionbinary[i_52+5]*(1<<32) + col52transactionbinary[i_52+6]*(1<<40) + col52transactionbinary[i_52+7]*(1<<48) + col52transactionbinary[i_52+8]*(1<<56)
                                                            i_52 += 9
                                                        elif col52transactionbinary[i_52] == b'\xfe'[0]:
                                                            v1_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24)
                                                            i_52 += 5
                                                        elif col52transactionbinary[i_52] == b'\xfd'[0]:
                                                            v1_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8)
                                                            i_52 += 3
                                                        else:
                                                            v1_52 = col52transactionbinary[i_52]
                                                            i_52 += 1
                                                        j_52 = 0
                                                        while j_52 < v1_52:
                                                            i_52 += 32 #vin previous txid
                                                            i_52 += 4 #vin previous txid index
                                                            v1_56 = 0 #vin script len
                                                            if col52transactionbinary[i_52] == b'\xff'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24) + col52transactionbinary[i_52+5]*(1<<32) + col52transactionbinary[i_52+6]*(1<<40) + col52transactionbinary[i_52+7]*(1<<48) + col52transactionbinary[i_52+8]*(1<<56)
                                                                i_52 += 9
                                                            elif col52transactionbinary[i_52] == b'\xfe'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24)
                                                                i_52 += 5
                                                            elif col52transactionbinary[i_52] == b'\xfd'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8)
                                                                i_52 += 3
                                                            else:
                                                                v1_56 = col52transactionbinary[i_52]
                                                                i_52 += 1
                                                            i_52 += v1_56 #vin script sometimes coinbase
                                                            i_52 += 4 #vin sequenceno
                                                            j_52 += 1
                                                        v2_52 = 0 #transaction vout count
                                                        if col52transactionbinary[i_52] == b'\xff'[0]:
                                                            v2_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24) + col52transactionbinary[i_52+5]*(1<<32) + col52transactionbinary[i_52+6]*(1<<40) + col52transactionbinary[i_52+7]*(1<<48) + col52transactionbinary[i_52+8]*(1<<56)
                                                            i_52 += 9
                                                        elif col52transactionbinary[i_52] == b'\xfe'[0]:
                                                            v2_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24)
                                                            i_52 += 5
                                                        elif col52transactionbinary[i_52] == b'\xfd'[0]:
                                                            v2_52 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8)
                                                            i_52 += 3
                                                        else:
                                                            v2_52 = col52transactionbinary[i_52]
                                                            i_52 += 1
                                                        j_52 = 0
                                                        while j_52 < v2_52:
                                                            if j_52 == col44voutinteger:
                                                                col44valueintegersatoshis = col52transactionbinary[i_52] + col52transactionbinary[i_52+1]*(1<<8) + col52transactionbinary[i_52+2]*(1<<16) + col52transactionbinary[i_52+3]*(1<<24) + col52transactionbinary[i_52+4]*(1<<32) + col52transactionbinary[i_52+5]*(1<<40) + col52transactionbinary[i_52+6]*(1<<48) + col52transactionbinary[i_52+7]*(1<<56)
                                                                v1_60 = col44valueintegersatoshis
                                                                col44value = (str(v1_60//100000000)+'.'+str(v1_60%100000000//10000000)+str(v1_60%10000000//1000000)+str(v1_60%1000000//100000)+str(v1_60%100000//10000)+str(v1_60%10000//1000)+str(v1_60%1000//100)+str(v1_60%100//10)+str(v1_60%10)).encode()
                                                                col44valuestatus = b'ok'
                                                                break
                                                            i_52 += 8 #vout value
                                                            v1_56 = 0 #vout script len
                                                            if col52transactionbinary[i_52] == b'\xff'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24) + col52transactionbinary[i_52+5]*(1<<32) + col52transactionbinary[i_52+6]*(1<<40) + col52transactionbinary[i_52+7]*(1<<48) + col52transactionbinary[i_52+8]*(1<<56)
                                                                i_52 += 9
                                                            elif col52transactionbinary[i_52] == b'\xfe'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8) + col52transactionbinary[i_52+3]*(1<<16) + col52transactionbinary[i_52+4]*(1<<24)
                                                                i_52 += 5
                                                            elif col52transactionbinary[i_52] == b'\xfd'[0]:
                                                                v1_56 = col52transactionbinary[i_52+1] + col52transactionbinary[i_52+2]*(1<<8)
                                                                i_52 += 3
                                                            else:
                                                                v1_56 = col52transactionbinary[i_52]
                                                                i_52 += 1
                                                            i_52 += v1_56 #vout script
                                                            j_52 += 1
                                                        try:
                                                            col44addresslist = json.loads(col48data.decode())['result']['vout'][col44voutinteger]['scriptPubKey']['addresses']
                                                        except KeyError:
                                                            pass
                                                    else:
                                                        col44valuestatus = b'rpc response delivery status: ' + col48status
                                                except IndexError:
                                                    col44valuestatus = b'invalid raw tx received'
                                                except json.decoder.JSONDecodeError:
                                                    col44valuestatus = b'could not interpret rpc json response'
                                            if col44txid == b'0000000000000000000000000000000000000000000000000000000000000000' and col44vout == str((1<<32)-1).encode():
                                                responsepart4 += b' coinbase : ' + col44coinbase
                                                responsepart4 += b' sequence : ' + col44sequence + b' <br/>'
                                            else:
                                                responsepart4 += b' txid : <a href="/tx/' + col44txid + b'/">' + col44txid + b'</a>'
                                                responsepart4 += b' vout : ' + col44vout
                                                responsepart4 += b' scriptSig asm : ' + col44scriptsigasm
                                                if col44valuestatus == b'ok':
                                                    responsepart4 += b' value : ' + col44value
                                                    if col72vinsumintegerstatus == b'no errors':
                                                        col72vinsumintegersatoshis += col44valueintegersatoshis
                                                else:
                                                    responsepart4 += b' value : <span style="color:red;">' + col44valuestatus + b'</span>'
                                                    col72vinsumintegerstatus = col44valuestatus
                                                responsepart4 += b' sequence : ' + col44sequence
                                                try:
                                                    if col44addresslist != None:
                                                        v1_56 = len(col44addresslist)
                                                        responsepart4 += b' addresses :'
                                                        i_56 = 0
                                                        while i_56 < v1_56:
                                                            responsepart4 += b' <a href="/address/' + col44addresslist[i_56].encode() + b'/">' + col44addresslist[i_56].encode() + b'</a>'
                                                            i_56 += 1
                                                except TypeError:
                                                    pass
                                                responsepart4 += b' <br/>'
                                            responsepart3 += responsepart4
                                            j_40 += 1
                                        v2_40 = 0 #transaction vout count
                                        if transactionbinary[i_40] == b'\xff'[0]:
                                            v2_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24) + transactionbinary[i_40+5]*(1<<32) + transactionbinary[i_40+6]*(1<<40) + transactionbinary[i_40+7]*(1<<48) + transactionbinary[i_40+8]*(1<<56)
                                            i_40 += 9
                                        elif transactionbinary[i_40] == b'\xfe'[0]:
                                            v2_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24)
                                            i_40 += 5
                                        elif transactionbinary[i_40] == b'\xfd'[0]:
                                            v2_40 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8)
                                            i_40 += 3
                                        else:
                                            v2_40 = transactionbinary[i_40]
                                            i_40 += 1
                                        j_40 = 0
                                        transactionvoutcountinteger = v2_40
                                        transactionvoutcount = str(transactionvoutcountinteger).encode()
                                        transactionvoutcountstatus = b'ok'
                                        responsepart3 += b' <b>Vout Count</b>: ' + transactionvoutcount + b' <br/>'
                                        while j_40 < v2_40:
                                            responsepart4 = b''
                                            col44valueintegersatoshis = 0
                                            col44value = b''
                                            col44n = str(j_40).encode()
                                            col44scriptpubkeyasm = b''
                                            col44valueintegersatoshis = transactionbinary[i_40] + transactionbinary[i_40+1]*(1<<8) + transactionbinary[i_40+2]*(1<<16) + transactionbinary[i_40+3]*(1<<24) + transactionbinary[i_40+4]*(1<<32) + transactionbinary[i_40+5]*(1<<40) + transactionbinary[i_40+6]*(1<<48) + transactionbinary[i_40+7]*(1<<56)
                                            v1_44 = col44valueintegersatoshis
                                            col44value = (str(v1_44//100000000)+'.'+str(v1_44%100000000//10000000)+str(v1_44%10000000//1000000)+str(v1_44%1000000//100000)+str(v1_44%100000//10000)+str(v1_44%10000//1000)+str(v1_44%1000//100)+str(v1_44%100//10)+str(v1_44%10)).encode()
                                            i_40 += 8 #vout value
                                            v2_44 = 0 #vout script len
                                            if transactionbinary[i_40] == b'\xff'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24) + transactionbinary[i_40+5]*(1<<32) + transactionbinary[i_40+6]*(1<<40) + transactionbinary[i_40+7]*(1<<48) + transactionbinary[i_40+8]*(1<<56)
                                                i_40 += 9
                                            elif transactionbinary[i_40] == b'\xfe'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8) + transactionbinary[i_40+3]*(1<<16) + transactionbinary[i_40+4]*(1<<24)
                                                i_40 += 5
                                            elif transactionbinary[i_40] == b'\xfd'[0]:
                                                v2_44 = transactionbinary[i_40+1] + transactionbinary[i_40+2]*(1<<8)
                                                i_40 += 3
                                            else:
                                                v2_44 = transactionbinary[i_40]
                                                i_40 += 1
                                            k_44 = i_40
                                            while k_44 < i_40 + v2_44:
                                                if col44scriptpubkeyasm:
                                                    col44scriptpubkeyasm += b' '
                                                if transactionbinary[k_44] == 0:
                                                    col44scriptpubkeyasm += b'OP_FALSE'
                                                    k_44 += 1
                                                elif 1 <= transactionbinary[k_44] and transactionbinary[k_44] <= 75:
                                                    if k_44 + 1 + transactionbinary[k_44] < i_40 + v2_44:
                                                        col44scriptpubkeyasm += transactionbinary[k_44+1:k_44+1+transactionbinary[k_44]].hex().encode()
                                                        k_44 += 1 + transactionbinary[k_44]
                                                    else:
                                                        col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                        break
                                                elif transactionbinary[k_44] == 76:
                                                    if k_44 + 1 < i_40 + v2_44:
                                                        if k_44 + 1 + transactionbinary[k_44+1] < i_40 + v2_44:
                                                            col44scriptpubkeyasm += b'OP_PUSHDATA1 ' + transactionbinary[k_44+2:k_44+2+transactionbinary[k_44+1]].hex().encode()
                                                            k_44 += 2 + transactionbinary[k_44+1]
                                                        else:
                                                            col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                            break
                                                    else:
                                                        col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                        break
                                                elif transactionbinary[k_44] == 77:
                                                    if k_44 + 2 < i_40 + v2_44:
                                                        if k_44 + 2 + transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8) < i_40 + v2_44:
                                                            col44scriptpubkeyasm += b'OP_PUSHDATA2 ' + transactionbinary[k_44+3:k_44+3+transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8)].hex().encode()
                                                            k_44 += 3 + transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8)
                                                        else:
                                                            col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                            break
                                                    else:
                                                        col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                        break
                                                elif transactionbinary[k_44] == 78:
                                                    if k_44 + 4 < i_40 + v2_44:
                                                        if k_44 + 4 + transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8) + transactionbinary[k_44+3] * (1<<16) + transactionbinary[k_44+4] * (1<<24) < i_40 + v2_44:
                                                            col44scriptpubkeyasm += b'OP_PUSHDATA4 ' + transactionbinary[k_44+5:k_44+5+transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8) + transactionbinary[k_44+3] * (1<<16) + transactionbinary[k_44+4] * (1<<24)].hex().encode()
                                                            k_44 += 5 + transactionbinary[k_44+1] + transactionbinary[k_44+2] * (1<<8) + transactionbinary[k_44+3] * (1<<16) + transactionbinary[k_44+4] * (1<<24)
                                                        else:
                                                            col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                            break
                                                    else:
                                                        col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                        break
                                                elif transactionbinary[k_44] == 79:
                                                    col44scriptpubkeyasm += b'OP_1NEGATE'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 80:
                                                    col44scriptpubkeyasm += b'OP_RESERVED'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 81:
                                                    col44scriptpubkeyasm += b'OP_TRUE'
                                                    k_44 += 1
                                                elif 82 <= transactionbinary[k_44] and transactionbinary[k_44] <= 96:
                                                    col44scriptpubkeyasm += b'OP_' + str(transactionbinary[k_44] - 80).encode()
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 97:
                                                    col44scriptpubkeyasm += b'OP_NOP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 98:
                                                    col44scriptpubkeyasm += b'OP_VER'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 99:
                                                    col44scriptpubkeyasm += b'OP_IF'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 100:
                                                    col44scriptpubkeyasm += b'OP_NOTIF'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 101:
                                                    col44scriptpubkeyasm += b'OP_VERIF'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 102:
                                                    col44scriptpubkeyasm += b'OP_VERNOTIF'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 103:
                                                    col44scriptpubkeyasm += b'OP_ELSE'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 104:
                                                    col44scriptpubkeyasm += b'OP_ENDIF'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 105:
                                                    col44scriptpubkeyasm += b'OP_VERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 106:
                                                    col44scriptpubkeyasm += b'OP_RETURN'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 107:
                                                    col44scriptpubkeyasm += b'OP_TOALTSTACK'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 108:
                                                    col44scriptpubkeyasm += b'OP_FROMALTSTACK'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 109:
                                                    col44scriptpubkeyasm += b'OP_2DROP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 110:
                                                    col44scriptpubkeyasm += b'OP_2DUP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 111:
                                                    col44scriptpubkeyasm += b'OP_3DUP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 112:
                                                    col44scriptpubkeyasm += b'OP_2OVER'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 113:
                                                    col44scriptpubkeyasm += b'OP_2ROT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 114:
                                                    col44scriptpubkeyasm += b'OP_2SWAP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 115:
                                                    col44scriptpubkeyasm += b'OP_IFDUP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 116:
                                                    col44scriptpubkeyasm += b'OP_DEPTH'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 117:
                                                    col44scriptpubkeyasm += b'OP_DROP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 118:
                                                    col44scriptpubkeyasm += b'OP_DUP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 119:
                                                    col44scriptpubkeyasm += b'OP_NIP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 120:
                                                    col44scriptpubkeyasm += b'OP_OVER'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 121:
                                                    col44scriptpubkeyasm += b'OP_PICK'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 122:
                                                    col44scriptpubkeyasm += b'OP_ROLL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 123:
                                                    col44scriptpubkeyasm += b'OP_ROT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 124:
                                                    col44scriptpubkeyasm += b'OP_SWAP'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 125:
                                                    col44scriptpubkeyasm += b'OP_TUCK'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 126:
                                                    col44scriptpubkeyasm += b'OP_CAT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 127:
                                                    col44scriptpubkeyasm += b'OP_SUBSTR'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 128:
                                                    col44scriptpubkeyasm += b'OP_LEFT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 129:
                                                    col44scriptpubkeyasm += b'OP_RIGHT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 130:
                                                    col44scriptpubkeyasm += b'OP_SIZE'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 131:
                                                    col44scriptpubkeyasm += b'OP_INVERT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 132:
                                                    col44scriptpubkeyasm += b'OP_AND'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 133:
                                                    col44scriptpubkeyasm += b'OP_OR'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 134:
                                                    col44scriptpubkeyasm += b'OP_XOR'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 135:
                                                    col44scriptpubkeyasm += b'OP_EQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 136:
                                                    col44scriptpubkeyasm += b'OP_EQUALVERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 137:
                                                    col44scriptpubkeyasm += b'OP_RESERVED1'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 138:
                                                    col44scriptpubkeyasm += b'OP_RESERVED2'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 139:
                                                    col44scriptpubkeyasm += b'OP_1ADD'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 140:
                                                    col44scriptpubkeyasm += b'OP_1SUB'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 141:
                                                    col44scriptpubkeyasm += b'OP_2MUL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 142:
                                                    col44scriptpubkeyasm += b'OP_2DIV'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 143:
                                                    col44scriptpubkeyasm += b'OP_NEGATE'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 144:
                                                    col44scriptpubkeyasm += b'OP_ABS'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 145:
                                                    col44scriptpubkeyasm += b'OP_NOT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 146:
                                                    col44scriptpubkeyasm += b'OP_0NOTEQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 147:
                                                    col44scriptpubkeyasm += b'OP_ADD'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 148:
                                                    col44scriptpubkeyasm += b'OP_SUB'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 149:
                                                    col44scriptpubkeyasm += b'OP_MUL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 150:
                                                    col44scriptpubkeyasm += b'OP_DIV'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 151:
                                                    col44scriptpubkeyasm += b'OP_MOD'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 152:
                                                    col44scriptpubkeyasm += b'OP_LSHIFT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 153:
                                                    col44scriptpubkeyasm += b'OP_RSHIFT'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 154:
                                                    col44scriptpubkeyasm += b'OP_BOOLAND'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 155:
                                                    col44scriptpubkeyasm += b'OP_BOOLOR'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 156:
                                                    col44scriptpubkeyasm += b'OP_NUMEQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 157:
                                                    col44scriptpubkeyasm += b'OP_NUMEQUALVERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 158:
                                                    col44scriptpubkeyasm += b'OP_NUMNOTEQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 159:
                                                    col44scriptpubkeyasm += b'OP_LESSTHAN'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 160:
                                                    col44scriptpubkeyasm += b'OP_GREATERTHAN'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 161:
                                                    col44scriptpubkeyasm += b'OP_LESSTHANOREQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 162:
                                                    col44scriptpubkeyasm += b'OP_GREATERTHANOREQUAL'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 163:
                                                    col44scriptpubkeyasm += b'OP_MIN'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 164:
                                                    col44scriptpubkeyasm += b'OP_MAX'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 165:
                                                    col44scriptpubkeyasm += b'OP_WITHIN'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 166:
                                                    col44scriptpubkeyasm += b'OP_RIPEMD160'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 167:
                                                    col44scriptpubkeyasm += b'OP_SHA1'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 168:
                                                    col44scriptpubkeyasm += b'OP_SHA256'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 169:
                                                    col44scriptpubkeyasm += b'OP_HASH160'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 170:
                                                    col44scriptpubkeyasm += b'OP_HASH256'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 171:
                                                    col44scriptpubkeyasm += b'OP_CODESEPARATOR'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 172:
                                                    col44scriptpubkeyasm += b'OP_CHECKSIG'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 173:
                                                    col44scriptpubkeyasm += b'OP_CHECKSIGVERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 174:
                                                    col44scriptpubkeyasm += b'OP_CHECKMULTISIG'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 175:
                                                    col44scriptpubkeyasm += b'OP_CHECKMULTISIGVERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 176:
                                                    col44scriptpubkeyasm += b'OP_NOP1'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 177:
                                                    col44scriptpubkeyasm += b'OP_CHECKLOCKTIMEVERIFY'
                                                    k_44 += 1
                                                elif transactionbinary[k_44] == 178:
                                                    col44scriptpubkeyasm += b'OP_CHECKSEQUENCEVERIFY'
                                                    k_44 += 1
                                                elif 179 <= transactionbinary[k_44] and transactionbinary[k_44] <= 185:
                                                    col44scriptpubkeyasm += b'OP_NOP' + str(transactionbinary[k_44] - 175).encode()
                                                    k_44 += 1
                                                else:
                                                    col44scriptpubkeyasm += b'?' + transactionbinary[k_44:i_40 + v2_44].hex().encode()
                                                    break
                                            i_40 += v2_44 #vout script
                                            responsepart4 += b' value : ' + col44value
                                            if col72voutsumintegerstatus == b'no errors':
                                                col72voutsumintegersatoshis += col44valueintegersatoshis
                                            responsepart4 += b' n : ' + col44n
                                            responsepart4 += b' scriptPubKey asm : ' + col44scriptpubkeyasm
                                            try:
                                                v1_48 = len(col32jsondata['result']['vout'][j_40]['scriptPubKey']['addresses'])
                                                responsepart4 += b' addresses :'
                                                i_48 = 0
                                                while i_48 < v1_48:
                                                    v1_52 = col32jsondata['result']['vout'][j_40]['scriptPubKey']['addresses'][i_48].encode()
                                                    responsepart4 += b' <a href="/address/' + v1_52 + b'/">' + v1_52 + b'</a>'
                                                    i_48 += 1
                                            except KeyError:
                                                pass
                                            except AttributeError:
                                                pass
                                            responsepart3 += responsepart4 + b' <br/>'
                                            j_40 += 1
                                    except IndexError:
                                        transactionvincountstatus = b'invalid raw tx received'
                                        transactionvoutcountstatus = b'invalid raw tx received'
                                        responsepart3 += b' <b>Vin Count</b>: <span style="color:red;">' + transactionvincountstatus + b'</span> <br/>'
                                        responsepart3 += b' <b>Vout Count</b>: <span style="color:red;">' + transactionvoutcountstatus + b'</span> <br/>'
                                else:
                                    if transactionvincountstatus == b'ok':
                                        responsepart3 += b' <b>Vin Count</b>: ' + transactionvincount + b' <br/>'
                                        col76_i = 0
                                        transactionvincountinteger = len(col32jsondata['result']['vin'])
                                        while col76_i < transactionvincountinteger:
                                            col80status = b'no errors'
                                            col80unescapedcoinbase = b''
                                            col80unescapedcoinbasestatus = b'not processed'
                                            col80txid = b''
                                            col80txidstatus = b'not processed'
                                            col80vout = b''
                                            col80voutinteger = 0
                                            col80voutstatus = b'not processed'
                                            col80scriptsigasm = b''
                                            col80scriptsigasmstatus = b'not processed'
                                            col80sequence = b''
                                            col80sequencestatus = b'not processed'
                                            col80valueintegersatoshis = 0
                                            col80value = b''
                                            col80valuestatus = b'not processed'
                                            responsepart4 = b''
                                            try:
                                                col80sequence = hex(col32jsondata['result']['vin'][col76_i]['sequence']).encode()
                                                col80sequencestatus = b'ok'
                                                col80txid = col32jsondata['result']['vin'][col76_i]['txid'].encode()
                                                col80txidstatus = b'ok'
                                                col80voutinteger = col32jsondata['result']['vin'][col76_i]['vout']
                                                col80vout = str(col80voutinteger).encode()
                                                col80voutstatus = b'ok'
                                                col80scriptsigasm = col32jsondata['result']['vin'][col76_i]['scriptSig']['asm'].encode()
                                                col80scriptsigasmstatus = b'ok'
                                                try:
                                                    col88status, col88data, col88queue = txresponsemap[col80txid]
                                                    if col88queue:
                                                        col88status, col88data = col88queue.get()
                                                        col88queue = None
                                                        txresponsemap[col80txid] = col88status, col88data, col88queue
                                                    if col88status == b'received':
                                                        col92jsondata = json.loads(col88data.decode())
                                                        try:
                                                            col96_i = 0
                                                            col96len = len(col92jsondata['result']['vout'])
                                                            col96status = b'not processed'
                                                            while col96_i < col96len:
                                                                if col92jsondata['result']['vout'][col96_i]['n'] == col80voutinteger:
                                                                    col80valueintegersatoshis = int(col92jsondata['result']['vout'][col96_i]['value'] * 100000000)
                                                                    v1_68 = col80valueintegersatoshis
                                                                    col80value = (str(v1_68//100000000)+'.'+str(v1_68%100000000//10000000)+str(v1_68%10000000//1000000)+str(v1_68%1000000//100000)+str(v1_68%100000//10000)+str(v1_68%10000//1000)+str(v1_68%1000//100)+str(v1_68%100//10)+str(v1_68%10)).encode()
                                                                    col96status = b'ok'
                                                                    break
                                                                col96_i += 1
                                                            if col96status == b'ok':
                                                                col80valuestatus = b'ok'
                                                            else:
                                                                col80valuestatus = b'input found ' + col96status
                                                        except KeyError:
                                                            col80valuestatus = b'input found not processed'
                                                        except TypeError:
                                                            col80valuestatus = b'input found not processed'
                                                            try:
                                                                col80valuestatus = b'rpc json error message: ' + col92jsondata['error']['message'].encode()
                                                            except TypeError:
                                                                pass
                                                        except IndexError:
                                                            col80valuestatus = b'input found invalid'
                                                    else:
                                                        col80valuestatus = b'rpc response delivery status: ' + col88status
                                                except json.decoder.JSONDecodeError:
                                                    col80valuestatus = b'could not interpret rpc json response, col88data = ' + col88data.__repr__().encode()
                                                except KeyError:
                                                    col80valuestatus = b'input not found'
                                                except ValueError:
                                                    col80valuestatus = b'txresponsemap bug'
                                            except KeyError:
                                                try:
                                                    col80unescapedcoinbase = col32jsondata['result']['vin'][col76_i]['coinbase'].encode()
                                                    col80unescapedcoinbasestatus = b'ok'
                                                except KeyError:
                                                    col80status = b'unknown vin type'
                                            except AttributeError:
                                                col80status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                            if col80status == b'no errors':
                                                if col80unescapedcoinbasestatus == b'ok':
                                                    col72isacoinbasetx = True
                                                    col88escapedcoinbase = b''
                                                    col88unescapedcoinbaselen = len(col80unescapedcoinbase)
                                                    col88_i = 0
                                                    col88status = b'no failures'
                                                    while (col88_i + 1) < col88unescapedcoinbaselen:
                                                        col92byte = bytes.fromhex(col80unescapedcoinbase[col88_i:col88_i+2].decode())
                                                        if col92byte == b'"':
                                                            col88escapedcoinbase += b'&quot;'
                                                        elif col92byte == b'&':
                                                            col88escapedcoinbase += b'&amp;'
                                                        elif col92byte == b"'":
                                                            col88escapedcoinbase += b'&apos;'
                                                        elif col92byte == b'<':
                                                            col88escapedcoinbase += b'&lt;'
                                                        elif col92byte == b'>':
                                                            col88escapedcoinbase += b'&gt;'
                                                        elif b' ' <= col92byte and col92byte <= b'~':
                                                            col88escapedcoinbase += col92byte
                                                        else:
                                                            col88escapedcoinbase += b'\\x' + col80unescapedcoinbase[col88_i:col88_i+2]
                                                        col88_i += 2
                                                    if col88status == b'no failures':
                                                        col80unescapedcoinbasestatus = b'ok'
                                                    else:
                                                        col80unescapedcoinbasestatus = col84status
                                                    if col80unescapedcoinbasestatus == b'ok':
                                                        responsepart4 += b' coinbase : ' + col88escapedcoinbase
                                                    else:
                                                        responsepart4 += b' coinbase : <span style="color:red;">' + col80unescapedcoinbasestatus + b'</span>'
                                                    if col80sequencestatus == b'ok':
                                                        responsepart4 += b' sequence : ' + col80sequence + b' <br/>'
                                                    else:
                                                        responsepart4 += b' sequence : <span style="color:red;">' + col80sequencestatus + b'</span> <br/>'
                                                else:
                                                    if col80txidstatus == b'ok':
                                                        responsepart4 += b' txid : <a href="/tx/' + col80txid + b'/">' + col80txid + b'</a>'
                                                    else:
                                                        responsepart4 += b' txid : <span style="color:red;">' + col80txidstatus + b'</span>'
                                                    if col80voutstatus == b'ok':
                                                        responsepart4 += b' vout : ' + col80vout
                                                    else:
                                                        responsepart4 += b' vout : <span style="color:red;">' + col80voutstatus + b'</span>'
                                                    if col80scriptsigasmstatus == b'ok':
                                                        responsepart4 += b' scriptSig asm : ' + col80scriptsigasm
                                                    else:
                                                        responsepart4 += b' scriptSig asm : <span style="color:red;">' + col80scriptsigasmstatus + b'</span>'
                                                    if col80valuestatus == b'ok':
                                                        responsepart4 += b' value : ' + col80value
                                                        if col72vinsumintegerstatus == b'no errors':
                                                            col72vinsumintegersatoshis += col80valueintegersatoshis
                                                    else:
                                                        responsepart4 += b' value : <span style="color:red;">' + col80valuestatus + b'</span>'
                                                        col72vinsumintegerstatus = col80valuestatus
                                                    if col80sequencestatus == b'ok':
                                                        responsepart4 += b' sequence : ' + col80sequence + b' <br/>'
                                                    else:
                                                        responsepart4 += b' sequence : <span style="color:red;">' + col80sequencestatus + b'</span> <br/>'
                                            else:
                                                responsepart4 += b' <span style="color:red;">' + col80status + b'</span> <br/>'
                                            responsepart3 += responsepart4
                                            col76_i += 1
                                    else:
                                        responsepart3 += b' <b>Vin Count</b>: <span style="color:red;">' + transactionvincountstatus + b'</span> <br/>'
                                        col72vinsumintegerstatus = transactionvincountstatus
                                    if transactionvoutcountstatus == b'ok':
                                        responsepart3 += b' <b>Vout Count</b>: ' + transactionvoutcount + b' <br/>'
                                        col76_i = 0
                                        transactionvoutcountinteger = len(col32jsondata['result']['vout'])
                                        while col76_i < transactionvoutcountinteger:
                                            responsepart4 = b''
                                            col80valueintegersatoshis = 0
                                            col80value = b''
                                            col80valuestatus = b'not processed'
                                            col80n = b''
                                            col80nstatus = b'not processed'
                                            col80scriptpubkeyasm = b''
                                            col80scriptpubkeyasmstatus = b'not processed'
                                            try:
                                                col80valueintegersatoshis = int(col32jsondata['result']['vout'][col76_i]['value'] * 100000000)
                                                v1_48 = col80valueintegersatoshis
                                                col80value = (str(v1_48//100000000)+'.'+str(v1_48%100000000//10000000)+str(v1_48%10000000//1000000)+str(v1_48%1000000//100000)+str(v1_48%100000//10000)+str(v1_48%10000//1000)+str(v1_48%1000//100)+str(v1_48%100//10)+str(v1_48%10)).encode()
                                                col80valuestatus = b'ok'
                                                col80ninteger = col32jsondata['result']['vout'][col76_i]['n']
                                                col80n = str(col80ninteger).encode()
                                                col80nstatus = b'ok'
                                                col80scriptpubkeyasm = col32jsondata['result']['vout'][col76_i]['scriptPubKey']['asm'].encode()
                                                if col80scriptpubkeyasm == b'OP_RETURN [error]':
                                                    try:
                                                        col80scriptpubkeyasm = b'OP_RETURN ' + col32jsondata['result']['vout'][col76_i]['scriptPubKey']['hex'].encode()[4:]
                                                    except KeyError:
                                                        pass
                                                    except TypeError:
                                                        pass
                                                col80scriptpubkeyasmstatus = b'ok'
                                            except KeyError:
                                                col80status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                                            if col80valuestatus == b'ok':
                                                responsepart4 += b' value : ' + col80value
                                                if col72voutsumintegerstatus == b'no errors':
                                                    col72voutsumintegersatoshis += col80valueintegersatoshis
                                            else:
                                                responsepart4 += b' value : <span style="color:red;">' + col80valuestatus + b'</span>'
                                                col72voutsumintegerstatus = col80valuestatus
                                            if col80nstatus == b'ok':
                                                responsepart4 += b' n : ' + col80n
                                            else:
                                                responsepart4 += b' n : <span style="color:red;">' + col80nstatus + b'</span>'
                                            if col80scriptpubkeyasmstatus == b'ok':
                                                responsepart4 += b' scriptPubKey asm : ' + col80scriptpubkeyasm
                                            else:
                                                responsepart4 += b' scriptPubKey asm : <span style="color:red;">' + col80scriptpubkeyasmstatus + b'</span>'
                                            try:
                                                col88addresscount = len(col32jsondata['result']['vout'][col76_i]['scriptPubKey']['addresses'])
                                                responsepart4 += b' addresses :'
                                                col84_i = 0
                                                while col84_i < col88addresscount:
                                                    col88address = col32jsondata['result']['vout'][col76_i]['scriptPubKey']['addresses'][col84_i].encode()
                                                    responsepart4 += b' <a href="/address/' + col88address + b'/">' + col88address + b'</a>'
                                                    col84_i += 1
                                            except KeyError:
                                                pass
                                            except AttributeError:
                                                pass
                                            responsepart3 += responsepart4 + b' <br/>'
                                            col76_i += 1
                                    else:
                                        responsepart3 += b' <b>Vout Count</b>: <span style="color:red;">' + transactionvoutcountstatus + b'</span> <br/>'
                                if transactionblockhashstatus == b'ok':
                                    responsepart3 += b' <b>Block Hash</b>: <a href="/getblockbyhash/' + transactionblockhash + b'/">' + transactionblockhash + b'</a> <br/>'
                                else:
                                    responsepart3 += b' <b>Block Hash</b>: <span style="color:red;">' + transactionblockhashstatus + b'</span> <br/>'
                                if transactionconfirmationsstatus == b'ok':
                                    responsepart3 += b' <b>Confirmations</b>: ' + transactionconfirmations + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Confirmations</b>: <span style="color:red;">' + transactionconfirmationsstatus + b'</span> <br/>'
                                if transactiontimestatus == b'ok':
                                    responsepart3 += b' <b>Time</b>: ' + transactiontime + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Time</b>: <span style="color:red;">' + transactiontimestatus + b'</span> <br/>'
                                if transactionblocktimestatus == b'ok':
                                    responsepart3 += b' <b>Block Time</b>: ' + transactionblocktime + b' <br/>'
                                else:
                                    responsepart3 += b' <b>Block Time</b>: <span style="color:red;">' + transactionblocktimestatus + b'</span> <br/>'
                                transactionfeeintegersatoshis = 0
                                transactionfee = b''
                                transactionfeestatus = b'not processed'
                                if col72vinsumintegerstatus == b'no errors' and col72voutsumintegerstatus == b'no errors':
                                    if col72vinsumintegersatoshis >= col72voutsumintegersatoshis:
                                        transactionfeeintegersatoshis = col72vinsumintegersatoshis - col72voutsumintegersatoshis
                                        v1_40 = transactionfeeintegersatoshis
                                        transactionfee = (str(v1_40//100000000)+'.'+str(v1_40%100000000//10000000)+str(v1_40%10000000//1000000)+str(v1_40%1000000//100000)+str(v1_40%100000//10000)+str(v1_40%10000//1000)+str(v1_40%1000//100)+str(v1_40%100//10)+str(v1_40%10)).encode()
                                        transactionfeestatus = b'ok'
                                    else:
                                        transactionfeestatus = b'vin sum ' + str(col72vinsumintegersatoshis).encode() + b' below vout sum ' + str(col72voutsumintegersatoshis).encode()
                                else:
                                    transactionfeestatus = b'vin sum status: ' + col72vinsumintegerstatus + b', vout sum status: ' + col72voutsumintegerstatus
                                if transactionfeestatus == b'ok':
                                    responsepart3 += b' <b>Fee</b>: ' + transactionfee + b' <br/>'
                                    if txfeesumintegerstatus == b'no errors':
                                        txfeesumintegersatoshis += transactionfeeintegersatoshis
                                elif col72isacoinbasetx:
                                    responsepart3 += b''
                                else:
                                    responsepart3 += b' <b>Fee</b>: <span style="color:red;">' + transactionfeestatus + b'</span> <br/>'
                                    txfeesumintegerstatus = transactionfeestatus
                                if transactionsizeintegerstatus == b'ok' and transactionfeestatus == b'ok':
                                    txsizefeepairs += [(transactionsizeinteger, transactionfeeintegersatoshis)]
                            except json.decoder.JSONDecodeError:
                                col24status = b'could not interpret rpc json response, col64rpcdata = ' + col24rpcdata.__repr__().encode()
##                            except KeyError:
##                                col24status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
##                                try:
##                                    col24status = b'rpc json error message: ' + json.loads(col24rpcdata.decode())['error']['message'].encode()
##                                except TypeError:
##                                    pass
##                            except AttributeError:
##                                col24status = b'unexpected rpc json response structure (' + str(inspect.getframeinfo(inspect.currentframe()).lineno).encode() + b')'
                        else:
                            col24status = b'rpc response delivery status: ' + col24rpcstatus
                        if col24status != b'no errors':
                            responsepart2 += b' <b>Error processing transaction: <span style="color:red;">' + col24status + b'</span></b> <br/>'
                    except ValueError:
                        col64txid, = returnedtxlist[j]
                        responsepart3 = b' <a href="/tx/' + col64txid + b'/">' + col64txid + b'</a> <br/>'
                    responsepart2_5 += responsepart3
                    j += 1
                txresponsemap = {}
                txsizefeepairslen = len(txsizefeepairs)
                # Windows 7 mspaint monochrome bitmap
                bmp_status = b'no errors'
                bmp_maxsize = 32
                bmp_maxfee = 32
                col56_i = 0
                while col56_i < txsizefeepairslen:
                    col60_size, col60_fee = txsizefeepairs[col56_i]
                    if bmp_maxsize < col60_size:
                        bmp_maxsize = col60_size
                    if bmp_maxfee < col60_fee:
                        bmp_maxfee = col60_fee
                    col56_i += 1
                bmp_x = 32
                bmp_y = 32
                bmp_xscaleexp = 0
                bmp_yscaleexp = 0
                if (bmp_maxsize + 1) <= 1024:
                    if (bmp_maxsize + 1) > 32:
                        bmp_x = bmp_maxsize + 1
                else:
                    while (bmp_maxsize >> bmp_xscaleexp) >= 1024:
                        bmp_xscaleexp += 1
                    if bmp_x <= (bmp_maxsize >> bmp_xscaleexp):
                        bmp_x = (bmp_maxsize >> bmp_xscaleexp) + 1
                if (bmp_maxfee + 1) <= 1024:
                    if (bmp_maxfee + 1) > 32:
                        bmp_y = bmp_maxfee + 1
                else:
                    while (bmp_maxfee >> bmp_yscaleexp) >= 1024:
                        bmp_yscaleexp += 1
                    if bmp_y <= (bmp_maxfee >> bmp_yscaleexp):
                        bmp_y = (bmp_maxfee >> bmp_yscaleexp) + 1
                bmp_dibsize = ((bmp_x + ((32 - (bmp_x & 31)) & 31)) * bmp_y) >> 3
                bmp_dibheader = b''
                bmp_dibheader += bytes([bmp_x & b'\xff'[0], (bmp_x >> 8) & b'\xff'[0], (bmp_x >> 16) & b'\xff'[0], (bmp_x >> 24) & b'\xff'[0]])
                bmp_dibheader += bytes([bmp_y & b'\xff'[0], (bmp_y >> 8) & b'\xff'[0], (bmp_y >> 16) & b'\xff'[0], (bmp_y >> 24) & b'\xff'[0]])
                bmp_dibheader += b'\x01\x00\x01\x00' + b'\x00\x00\x00\x00'
                bmp_dibheader += bytes([bmp_dibsize & b'\xff'[0], (bmp_dibsize >> 8) & b'\xff'[0], (bmp_dibsize >> 16) & b'\xff'[0], (bmp_dibsize >> 24) & b'\xff'[0]])
                bmp_dibheader += b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00'
                bmp_dibheaderlen = len(bmp_dibheader)
                bmp_headerlen = len(b'BM') + 4 + 4 + 4 + 4 + bmp_dibheaderlen + 4
                bmp_filelen = bmp_headerlen + bmp_dibsize
                bmp_header = b'BM'
                bmp_header += bytes([bmp_filelen & b'\xff'[0], (bmp_filelen >> 8) & b'\xff'[0], (bmp_filelen >> 16) & b'\xff'[0], (bmp_filelen >> 24) & b'\xff'[0]])
                bmp_header += b'\x00\x00\x00\x00'
                bmp_header += bytes([bmp_headerlen & b'\xff'[0], (bmp_headerlen >> 8) & b'\xff'[0], (bmp_headerlen >> 16) & b'\xff'[0], (bmp_headerlen >> 24) & b'\xff'[0]])
                bmp_header += bytes([bmp_dibheaderlen & b'\xff'[0], (bmp_dibheaderlen >> 8) & b'\xff'[0], (bmp_dibheaderlen >> 16) & b'\xff'[0], (bmp_dibheaderlen >> 24)])
                bmp_header += bmp_dibheader
                bmp_header += b'\xff\xff\xff\x00'
                bmp_dib = bytearray(bmp_dibsize)

                # White bitmap
                try:
                    col60_i = 0
                    while col60_i < bmp_y:
                        col64_i = 0
                        while col64_i < bmp_x:
                            col68bitindex = col60_i * (bmp_x + ((32 - (bmp_x & 31)) & 31)) + col64_i
                            col68byte = bmp_dib[col68bitindex >> 3]
                            bmp_dib[col68bitindex >> 3] = col68byte | (1 << (7 - (col68bitindex & 7)))
                            col64_i += 1
                        col60_i += 1
                except IndexError:
                    bmp_status = b'corrupt bmp builder on whitening'
                col56_i = 0
                while col56_i < txsizefeepairslen and bmp_status == b'no errors':
                    col60_size, col60_fee = txsizefeepairs[col56_i]
                    try:
                        col64bitindex = (col60_fee >> bmp_yscaleexp) * (bmp_x + ((32 - (bmp_x & 31)) & 31)) + (col60_size >> bmp_xscaleexp)
                        col64byte = bmp_dib[col64bitindex >> 3]
                        bmp_dib[col64bitindex >> 3] = col64byte & (255 ^ (1 << (7 - (col64bitindex & 7))))
                    except IndexError:
                        bmp_status = b'corrupt bmp builder on dotting'
                        print('(col60_fee, col60_size, bmp_yscaleexp, bmp_xscaleexp, bmp_y, bmp_x, (col60_fee >> bmp_yscaleexp), (col60_size >> bmp_xscaleexp)) = ' + (col60_fee, col60_size, bmp_yscaleexp, bmp_xscaleexp, bmp_y, bmp_x, (col60_fee >> bmp_yscaleexp), (col60_size >> bmp_xscaleexp)).__repr__())
                        break
                    col56_i += 1
                bmp_file = bmp_header + bmp_dib
                if txfeesumintegerstatus == b'no errors':
                    v1_20 = txfeesumintegersatoshis
                    v2_20 = (str(v1_20//100000000)+'.'+str(v1_20%100000000//10000000)+str(v1_20%10000000//1000000)+str(v1_20%1000000//100000)+str(v1_20%100000//10000)+str(v1_20%10000//1000)+str(v1_20%1000//100)+str(v1_20%100//10)+str(v1_20%10)).encode()
                    responsepart2 += b' <b>Sum of expanded transaction fees</b>: ' + v2_20 + b' <br/>'
                else:
                    responsepart2 += b' <b>Sum of expanded transaction fees</b>: <span style="color:red;">' + txfeesumintegerstatus + b'</span> <br/>'
                if bmp_status == b'no errors':
                    responsepart2 += b' <b>Fee dependency on transaction size, x axis from 0 to ' + str(bmp_x << bmp_xscaleexp).encode() + b' bytes, y axis from 0 to ' + str(bmp_y << bmp_yscaleexp).encode() + b' satoshis (' + str((bmp_y << bmp_yscaleexp)/100000000).encode() + b' bitcoins ), one pixel ' + str(1 << bmp_xscaleexp).encode() + b' bytes, ' + str(1 << bmp_yscaleexp).encode() + b' satoshis</b>: <img src="data:image/bmp;base64,' + base64.b64encode(bmp_file) + b'" style="border: 1px solid black; background: red none repeat scroll 0% 0%; padding: 1px;"/> <br/>'
                else:
                    responsepart2 += b' <b>Fee dependency on transaction size</b>: <span style="color:red;">' + bmp_status + b'</span> <br/>'
                responsepart2 += responsepart2_5
            unescapedid = rpcsocketqueue.__repr__().encode()
            unescapedidlen = len(unescapedid)
            escapedid = b''
            i_j = 0
            while i_j < unescapedidlen:
                if unescapedid[i_j:i_j+1] == b'"':
                    escapedid += b'&quot;'
                elif unescapedid[i_j:i_j+1] == b'&':
                    escapedid += b'&amp;'
                elif unescapedid[i_j:i_j+1] == b"'":
                    escapedid += b'&apos;'
                elif unescapedid[i_j:i_j+1] == b'<':
                    escapedid += b'&lt;'
                elif unescapedid[i_j:i_j+1] == b'>':
                    escapedid += b'&gt;'
                else:
                    escapedid += unescapedid[i_j:i_j+1]
                i_j += 1
            col52family, ip, port = ipportpair
            responsepart = b' <b>Query result on endpoint ' + ip.encode() + b':' + str(port).encode() + b' bound to ' + escapedid + b'</b> <br/>' + responsepart2
            if responsepart == lastresponsepart:
                responsecontainer += b' <b><span style="color:green;">Duplicate content dropped from endpoint ' + ip.encode() + b':' + str(port).encode() + b'</span></b> <br/>'
            else:
                responsecontainer += responsepart
                lastresponsepart = responsepart
            i += 1               
        responsebody = b'<!DOCTYPE html>\r\n<html><head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\r\n<title>blockchainrpc 0.0 - blockchain explorer for bitcoin addrindex node</title></head>\r\n<body>\r\n<div id="blockchainrpc">' + responsecontainer + b'</div>\r\n</body>\r\n</html>'
        response = b''
        response += protocolstring + b' 200 OK\r\n'
        response += b'Cache-Control: no-cache, no-store, must-revalidate\r\n'
        response += b'Pragma: no-cache\r\n'
        response += b'Expires: 0\r\n'
        response += b'Content-Type: text/html\r\n'
        response += b'Content-Length: ' + str(len(responsebody)).encode() + b'\r\n'
        response += b'\r\n'
        if includebody:
            response += responsebody
        liveresponse[0] = response
        livelastactivity[0] = time.time()
        return
    liveresponse[0] = protocolstring + b' 204 No Content\r\n\r\n'
    livelastactivity[0] = time.time()
    
def blockingservercontentprovider(jobqueue):
    resourcemap = {}
    resourcedroptimeout = 2 * 60 * 60 * 1.0 #Unsent responses are dropped after two hours
    # Default behavior: Unsent responses are sent to matching client endpoint and dropped
    while True:
        currenttime = time.time()
        commandtype, resource, clientaddress, backlinkqueue = jobqueue.get()
        clientipaddress = None
        try:
            clientipaddress, x, y, z = clientaddress
        except ValueError:
            clientipaddress, x = clientaddress
        if commandtype == b'put':
            uriresource, postedcontent, serverparams, nextjobgroup = resource
            for v1_12, v2_12 in resourcemap.items():
                v1_16, v2_16, v3_16 = v1_12
                v4_16, v5_16 = v2_12
                v6_16, v7_16, v8_16 = v5_16
                if (v6_16, v7_16, v8_16) == (None, None, None):
                    try:
                        v6_16, v7_16, v8_16 = v4_16.get_nowait()
                    except queue.Empty:
                        pass
                if v8_16 != None and v8_16[0] != None and (v7_16[0] + resourcedroptimeout) < currenttime and (v1_16, v2_16, v3_16) != (uriresource, postedcontent, clientipaddress):
                    del resourcemap[v1_12]
                else:
                    v5_16 = v6_16, v7_16, v8_16
                    v2_12 = v4_16, v5_16
                    resourcemap[v1_12] = v2_12
            serverjob, = nextjobgroup
            serverjobqueue, serverjobpusher, futurejobs = serverjob
            #requestrpcjob, = futurejobs
            #requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets = requestrpcjob]
            serverqueue, serverlivedata = None, (None, None, None)
            serverlivefirstactivity, serverlivelastactivity, serverliveresponse = serverlivedata
            try:
                serverqueue, serverlivedata = resourcemap[(uriresource, postedcontent, clientipaddress)]
                serverlivefirstactivity, serverlivelastactivity, serverliveresponse = serverlivedata
            except KeyError:
                serverqueue = queue.Queue()
                if not serverjobpusher.is_alive():
                    try:
                        serverjobpusher.start()
                    except RuntimeError:
                        pass
                serverjobqueue.put((uriresource, postedcontent, serverparams, futurejobs, serverqueue))
            serverlivedata = serverlivefirstactivity, serverlivelastactivity, serverliveresponse
            resourcemap[(uriresource, postedcontent, clientipaddress)] = (serverqueue, serverlivedata)
            backlinkqueue.put((b'ok',))
            continue
        elif commandtype == b'get':
            uriresource, postedcontent, serverparams, nextjobgroup = resource
            for v1_12, v2_12 in resourcemap.items():
                v1_16, v2_16, v3_16 = v1_12
                v4_16, v5_16 = v2_12
                v6_16, v7_16, v8_16 = v5_16
                if (v6_16, v7_16, v8_16) == (None, None, None):
                    try:
                        v6_16, v7_16, v8_16 = v4_16.get_nowait()
                    except queue.Empty:
                        pass
                v5_16 = v6_16, v7_16, v8_16
                v2_12 = v4_16, v5_16
                resourcemap[v1_12] = v2_12
            #serverjob, = nextjobgroup
            #serverjobqueue, serverjobpusher, futurejobs = serverjob
            #requestrpcjob, = futurejobs
            #requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets = requestrpcjob
            serverlivefirstactivity, serverlivelastactivity, serverliveresponse = None, None, None
            serverqueue, serverlivedata = None, (None, None, None)
            try:
                serverqueue, serverlivedata = resourcemap[(uriresource, postedcontent, clientipaddress)]
                serverlivefirstactivity, serverlivelastactivity, serverliveresponse = serverlivedata
                if serverliveresponse != None and serverliveresponse[0] != None:
##                    print('provider: ', end='\r')
##                    print('provider: returning ' + serverliveresponse[0][0:].__repr__() + ' for ' + uriresource.__repr__())
                    backlinkqueue.put((b'ok', serverliveresponse[0][0:]))
                    del resourcemap[(uriresource, postedcontent, clientipaddress)]
                    continue
            except KeyError:
                backlinkqueue.put((b'gone', b''))
                continue
            backlinkqueue.put((b'processing', b''))
        elif commandtype == b'getlist':
            resourcemapdup = {}
            for v1_12, v2_12 in resourcemap.items():
                v1_16, v2_16, v3_16 = v1_12
                v4_16, v5_16 = v2_12
                v6_16, v7_16, v8_16 = v5_16
                v6_16dup, v7_16dup, v8_16dup = (None, None, None)
                if v6_16 != None:
                    v6_16dup = [v6_16[0]]
                if v7_16 != None:
                    v7_16dup = [v7_16[0]]
                if v8_16 != None:
                    v8_16dup = [v8_16[0]]
                v5_16dup = v6_16dup, v7_16dup, v8_16dup
                v2_12dup = v4_16, v5_16dup
                v1_12dup = v1_16, v2_16, v3_16
                resourcemapdup[v1_12dup] = v2_12dup
            backlinkqueue.put((b'', resourcemapdup))
            
def blockingprocessheaders(client, receivedheaderslist, nextjobgroup):
    #print('enter blockingprocessheaders(' + client.__repr__() + ', ' + receivedheaderslist.__repr__() + ', ' + nextjobgroup.__repr__() + ')')
    print(client.__repr__() + ' on blockingprocessheaders')
    #print('nextjobgroup = ' + nextjobgroup.__repr__())
    readdatajob, servercontentproviderjob, sendresponsejob = nextjobgroup
    #print('(readdatajob, servercontentproviderjob, sendresponsejob) = ' + (readdatajob, servercontentproviderjob, sendresponsejob).__repr__())
    readdatajobqueue, readdatajobpusher = readdatajob
    #print('(readdatajobqueue, readdatajobpusher) = ' + (readdatajobqueue, readdatajobpusher).__repr__())
    servercontentproviderjobqueue, servercontentproviderjobpusher, futurejobs = servercontentproviderjob
    #print('(servercontentproviderjobqueue, servercontentproviderjobpusher, futurejobs) = ' + (servercontentproviderjobqueue, servercontentproviderjobpusher, futurejobs).__repr__())
    sendresponsejobqueue, sendresponsejobpusher, socketrecyclequeue = sendresponsejob
    #print('(sendresponsejobqueue, sendresponsejobpusher, socketrecyclequeue) = ' + (sendresponsejobqueue, sendresponsejobpusher, socketrecyclequeue).__repr__())
    serverjob, = futurejobs
    #print('(serverjob,) = ' + (serverjob,).__repr__())
    serverjobqueue, serverjobpusher, farfuturejobs = serverjob
    #print('(serverjobqueue, serverjobpusher, farfuturejobs) = ' + (serverjobqueue, serverjobpusher, farfuturejobs).__repr__())
    requestrpcjob, = farfuturejobs
    #print('(requestrpcjob,) = ' + (requestrpcjob,).__repr__())
    requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets = requestrpcjob
    #print('(requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets) = ' + (requestrpcjobqueue, requestrpcjobpusher, requestrpcsockets).__repr__())
    headerlinecount = len(receivedheaderslist)
    if headerlinecount:
        firstheader = receivedheaderslist[0]
        firstheaderlen = len(firstheader)
        i = 0
        method = b''
        while i < firstheaderlen:
            byte = firstheader[i:i+1]
            if byte == b' ':
                #print(client.__repr__() + ' on blockingprocessheaders method checkpoint enter')
                resource = b''
                i += 1
                while i < firstheaderlen:
                    byte = firstheader[i:i+1]
                    if byte == b' ':
                        #print(client.__repr__() + ' on blockingprocessheaders resource checkpoint enter')
                        protocolversion = b''
                        i += 1
                        while i < firstheaderlen:
                            byte = firstheader[i:i+1]
                            if byte == b'\r':
                                #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 1 enter')
                                i += 1
                                if i < firstheaderlen:
                                    #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 2 enter')
                                    byte = firstheader[i:i+1]
                                    if byte == b'\n':
                                        #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 3 enter')
                                        if protocolversion == b'HTTP/1.1' or protocolversion == b'HTTP/1.0' or protocolversion == b'BLOCKCHAINRPC/0.0':
                                            print(client.__repr__() + ' on blockingprocessheaders protocol checkpoint enter')
                                            reusesocket = True
                                            if protocolversion == b'HTTP/1.0':
                                                reusesocket = False
                                            sendresponsebody = True
                                            if method == b'HEAD':
                                                sendresponsebody = False
                                            i = 1
                                            chunkedbody = False
                                            headerlinecount = len(receivedheaderslist)
                                            while i < headerlinecount:
                                                headerline = receivedheaderslist[i]
                                                headerlinelen = len(headerline)
                                                headerlined = b''
                                                j = 0
                                                while j < headerlinelen:
                                                    if b'a'[0] <= headerline[j] and headerline[j] <= b'z'[0]:
                                                        headerlined += bytes([headerline[j] - b'a'[0] + b'A'[0]])
                                                    elif headerline[j:j+1] != b' ':
                                                        headerlined += headerline[j:j+1]
                                                    j += 1
                                                if headerlined == b'CONNECTION:CLOSE':
                                                    reusesocket = False
                                                if headerlined == b'CONNECTION:KEEP-ALIVE':
                                                    reusesocket = True
                                                if headerlined == b'TRANSFER-ENCODING:CHUNKED':
                                                    chunkedbody = True
                                                i += 1
                                            hascontentlength = False
                                            contentlength = 0
                                            contentqueue = None
                                            i = 1
                                            while i < headerlinecount:
                                                headerline = receivedheaderslist[i]
                                                headerlinelen = len(headerline)
                                                headerkey = b''
                                                j = 0
                                                while j < headerlinelen:
                                                    if headerline[j:j+1] != b':':
                                                        if b'a'[0] <= headerline[j] and headerline[j] <= b'z'[0]:
                                                            headerkey += bytes([headerline[j] - b'a'[0] + b'A'[0]])
                                                        else:
                                                            headerkey += headerline[j:j+1]
                                                    else:
                                                        break
                                                    j += 1
                                                if headerkey == b'CONTENT-LENGTH':
                                                    hascontentlength = True
                                                    j += 1
                                                    while j < headerlinelen:
                                                        if b'0'[0] <= headerline[j] and headerline[j] <= b'9'[0]:
                                                            contentlength = contentlength * 10 + headerline[j] - b'0'[0]
                                                        j += 1
                                                i += 1
                                            if chunkedbody:
                                                contentqueue = queue.Queue()
                                                if not readdatajobpusher.is_alive():
                                                    try:
                                                        readdatajobpusher.start()
                                                    except RuntimeError:
                                                        pass
                                                readdatajobqueue.put((client, (contentlength, b'chunked'), contentqueue))
                                            elif not hascontentlength and method == b'POST':
                                                reusesocket = False
                                                contentqueue = queue.Queue()
                                                if not readdatajobpusher.is_alive():
                                                    try:
                                                        readdatajobpusher.start()
                                                    except RuntimeError:
                                                        pass
                                                readdatajobqueue.put((client, (None, ), contentqueue))
                                            elif contentlength:
                                                contentqueue = queue.Queue()
                                                if not readdatajobpusher.is_alive():
                                                    try:
                                                        readdatajobpusher.start()
                                                    except RuntimeError:
                                                        pass
                                                readdatajobqueue.put((client, (contentlength, ), contentqueue))
                                            content = b''
                                            if contentqueue:
                                                contentstatus, contentdata = contentqueue.get()
                                                if contentstatus == b'received':
                                                    content = contentdata
                                                else:
                                                    reusesocket = False
                                            timelimittarget = 5.0
                                            timeframestart = time.time()
                                            if not servercontentproviderjobpusher.is_alive():
                                                try:
                                                    servercontentproviderjobpusher.start()
                                                except RuntimeError:
                                                    pass
                                            providerqueue = queue.Queue()
                                            clientsocket, overpair, clientaddress = client[0]
                                            servercontentproviderjobqueue.put((b'put', (resource, content, (protocolversion, sendresponsebody), futurejobs), clientaddress, providerqueue))
                                            providerstatus = b'no errors'
                                            providerputstatus, = providerqueue.get()
                                            timeframeend = time.time()
                                            timeframe = int(timeframeend - timeframestart) + int(((timeframeend - timeframestart) - int(timeframeend - timeframestart)) * 1000) / 1000 + 0.001
                                            response = b''
                                            if providerputstatus == b'ok':
                                                i_48 = 0
                                                while True:
                                                    providergetqueue = queue.Queue()
                                                    servercontentproviderjobqueue.put((b'get', (resource, content, (protocolversion, sendresponsebody), futurejobs), clientaddress, providergetqueue))
                                                    providergetstatus, providergetdata = providergetqueue.get()
                                                    if providergetstatus == b'ok':
                                                        if not sendresponsejobpusher.is_alive():
                                                            try:
                                                                sendresponsejobpusher.start()
                                                            except RuntimeError:
                                                                pass
                                                        client[0] = clientsocket, overpair, clientaddress
##                                                        print('processheaders: ', end='\r')
##                                                        print('processheaders: got provider data ' + providergetdata.__repr__())
                                                        sendresponsejobqueue.put((client, providergetdata, reusesocket, socketrecyclequeue))
                                                        return
                                                    elif providergetstatus != b'processing':
                                                        providerstatus = b'providergetstatus ' + providergetstatus
                                                        break
                                                    if timeframe * (1 << i_48) < (timelimittarget + timeframe + 0.001):
                                                        time.sleep(timeframe * (1 << i_48))
                                                        i_48 += 1
                                                    else:
                                                        break
                                            if providerstatus == b'no errors':
                                                providergetlistqueue = queue.Queue()
                                                servercontentproviderjobqueue.put((b'getlist', (resource, content, (protocolversion, sendresponsebody), futurejobs), clientaddress, providergetlistqueue))
                                                providergetliststatus, providergetlistmap = providergetlistqueue.get()
                                                responsepart = b''
                                                for v1_48, v2_48 in providergetlistmap.items():
                                                    responsepart2 = b''
                                                    v1_52, v2_52, v3_52 = v1_48
                                                    v3_52 = v3_52.encode()
                                                    v4_52, v5_52 = v2_48
                                                    v6_52, v7_52, v8_52 = v5_52
                                                    v1_52len = len(v1_52)
                                                    i_52 = 0
                                                    v1_52encoded = b''
                                                    while i_52 < v1_52len:
                                                        if v1_52[i_52] == b'"'[0]:
                                                            v1_52encoded += b'&quot;'
                                                        elif v1_52[i_52] == b'&'[0]:
                                                            v1_52encoded += b'&amp;'
                                                        elif v1_52[i_52] == b"'"[0]:
                                                            v1_52encoded += b'&apos;'
                                                        elif v1_52[i_52] == b'<'[0]:
                                                            v1_52encoded += b'&lt;'
                                                        elif v1_52[i_52] == b'>'[0]:
                                                            v1_52encoded += b'&gt;'
                                                        elif b' '[0] <= v1_52[i_52] and v1_52[i_52] <= b'~'[0]:
                                                            v1_52encoded += bytes([v1_52[i_52]])
                                                        elif (v1_52[i_52] >> 4) > 9 and (v1_52[i_52] & 15) > 9:
                                                            v1_52encoded += b'\\x' + bytes([(v1_52[i_52] >> 4) - 10 + b'a'[0], (v1_52[i_52] & 15) - 10 + b'a'[0]])
                                                        elif (v1_52[i_52] >> 4) > 9:
                                                            v1_52encoded += b'\\x' + bytes([(v1_52[i_52] >> 4) - 10 + b'a'[0], (v1_52[i_52] & 15) + b'0'[0]])
                                                        elif (v1_52[i_52] & 15) > 9:
                                                            v1_52encoded += b'\\x' + bytes([(v1_52[i_52] >> 4) + b'0'[0], (v1_52[i_52] & 15) - 10 + b'a'[0]])
                                                        else:
                                                            v1_52encoded += b'\\x' + bytes([(v1_52[i_52] >> 4) + b'0'[0], (v1_52[i_52] & 15) + b'0'[0]])
                                                        i_52 += 1
                                                    if v1_52len:
                                                        responsepart2 += b' <b>Requested resource</b>: ' + v1_52encoded
                                                    v2_52len = len(v2_52)
                                                    i_52 = 0
                                                    v2_52encoded = b''
                                                    while i_52 < v2_52len:
                                                        if v2_52[i_52] == b'"'[0]:
                                                            v2_52encoded += b'&quot;'
                                                        elif v2_52[i_52] == b'&'[0]:
                                                            v2_52encoded += b'&amp;'
                                                        elif v2_52[i_52] == b"'"[0]:
                                                            v2_52encoded += b'&apos;'
                                                        elif v2_52[i_52] == b'<'[0]:
                                                            v2_52encoded += b'&lt;'
                                                        elif v2_52[i_52] == b'>'[0]:
                                                            v2_52encoded += b'&gt;'
                                                        elif b' '[0] <= v2_52[i_52] and v2_52[i_52] <= b'~'[0]:
                                                            v2_52encoded += bytes([v2_52[i_52]])
                                                        elif (v2_52[i_52] >> 4) > 9 and (v2_52[i_52] & 15) > 9:
                                                            v2_52encoded += b'\\x' + bytes([(v2_52[i_52] >> 4) - 10 + b'a'[0], (v2_52[i_52] & 15) - 10 + b'a'[0]])
                                                        elif (v2_52[i_52] >> 4) > 9:
                                                            v2_52encoded += b'\\x' + bytes([(v2_52[i_52] >> 4) - 10 + b'a'[0], (v2_52[i_52] & 15) + b'0'[0]])
                                                        elif (v2_52[i_52] & 15) > 9:
                                                            v2_52encoded += b'\\x' + bytes([(v2_52[i_52] >> 4) + b'0'[0], (v2_52[i_52] & 15) - 10 + b'a'[0]])
                                                        else:
                                                            v2_52encoded += b'\\x' + bytes([(v2_52[i_52] >> 4) + b'0'[0], (v2_52[i_52] & 15) + b'0'[0]])
                                                        i_52 += 1
                                                    if v2_52len:
                                                        responsepart2 += b' <b>Posted content</b>: ' + v2_52encoded
                                                    v3_52len = len(v3_52)
                                                    i_52 = 0
                                                    v3_52encoded = b''
                                                    while i_52 < v3_52len:
                                                        if v3_52[i_52] == b'"'[0]:
                                                            v3_52encoded += b'&quot;'
                                                        elif v3_52[i_52] == b'&'[0]:
                                                            v3_52encoded += b'&amp;'
                                                        elif v3_52[i_52] == b"'"[0]:
                                                            v3_52encoded += b'&apos;'
                                                        elif v3_52[i_52] == b'<'[0]:
                                                            v3_52encoded += b'&lt;'
                                                        elif v3_52[i_52] == b'>'[0]:
                                                            v3_52encoded += b'&gt;'
                                                        elif b' '[0] <= v3_52[i_52] and v3_52[i_52] <= b'~'[0]:
                                                            v3_52encoded += bytes([v3_52[i_52]])
                                                        elif (v3_52[i_52] >> 4) > 9 and (v3_52[i_52] & 15) > 9:
                                                            v3_52encoded += b'\\x' + bytes([(v3_52[i_52] >> 4) - 10 + b'a'[0], (v3_52[i_52] & 15) - 10 + b'a'[0]])
                                                        elif (v3_52[i_52] >> 4) > 9:
                                                            v3_52encoded += b'\\x' + bytes([(v3_52[i_52] >> 4) - 10 + b'a'[0], (v3_52[i_52] & 15) + b'0'[0]])
                                                        elif (v3_52[i_52] & 15) > 9:
                                                            v3_52encoded += b'\\x' + bytes([(v3_52[i_52] >> 4) + b'0'[0], (v3_52[i_52] & 15) - 10 + b'a'[0]])
                                                        else:
                                                            v3_52encoded += b'\\x' + bytes([(v3_52[i_52] >> 4) + b'0'[0], (v3_52[i_52] & 15) + b'0'[0]])
                                                        i_52 += 1
                                                    if v3_52len:
                                                        responsepart2 += b' <b>IP address</b>: ' + v3_52encoded
                                                    timeframestart = time.time()
                                                    if v6_52 != None and v6_52[0] != None:
                                                        responsepart2 += b' <b>First activity</b>: ' + str(timeframestart - v6_52[0]).encode() + b' sec ago'
                                                    if v7_52 != None and v7_52[0] != None:
                                                        responsepart2 += b' <b>Last activity</b>: ' + str(timeframestart - v7_52[0]).encode() + b' sec ago'
                                                    if v8_52 != None and v8_52[0] != None:
                                                        responsepart2 += b' <span style="color: green;">Response is available</span>'
                                                    responsepart2 += b' <br/>'
                                                    responsepart += responsepart2
                                                responsecontainer = b'<div>Requested resource is still being generated. This page will reload once a minute till resource is ready. <br/> See what others are waiting for: <br/>' + responsepart + b' </div>'
                                                responsebody = b'<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/><title>Requested resource is still processing...</title><meta http-equiv="refresh" content="60"/></head><body>' + responsecontainer + b'</body></html>'
                                                response = b''
                                                response += protocolversion + b' 200 OK\r\n'
                                                response += b'Cache-Control: no-cache, no-store, must-revalidate\r\n'
                                                response += b'Pragma: no-cache\r\n'
                                                response += b'Expires: 0\r\n'
                                                response += b'Content-Type: text/html\r\n'
                                                response += b'Content-Length: ' + str(len(responsebody)).encode() + b'\r\n'
                                                response += b'\r\n'
                                                if sendresponsebody:
                                                    response += responsebody
                                                if not sendresponsejobpusher.is_alive():
                                                    try:
                                                        sendresponsejobpusher.start()
                                                    except RuntimeError:
                                                        pass
                                                sendresponsejobqueue.put((client, response, reusesocket, socketrecyclequeue))
                                                print(client.__repr__() + ' on blockingprocessheaders resource checkpoint return')
                                                return
                                            else:
                                                providerstatus == b'providerputstatus ' + providerputstatus
                                            if not sendresponsejobpusher.is_alive():
                                                try:
                                                    sendresponsejobpusher.start()
                                                except RuntimeError:
                                                    pass
                                            sendresponsejobqueue.put((client, protocolversion + b' 500 Internal Server Error\r\nX-Error-Message: ' + providerstatus + b'\r\n\r\n', reusesocket, socketrecyclequeue))
                                            print(client.__repr__() + ' on blockingprocessheaders resource checkpoint return')
                                            return
                                        #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 3 leave')
                                    #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 2 leave')
                                #print(client.__repr__() + ' on blockingprocessheaders protocolversion checkpoint 1 leave')
                                break
                            else:
                                protocolversion += byte
                            i += 1
                        #print(client.__repr__() + ' on blockingprocessheaders resource checkpoint leave')
                        break
                    else:
                        resource += byte
                    i += 1
                #print(client.__repr__() + ' on blockingprocessheaders method checkpoint leave')
                break
            else:
                method += byte
            i += 1
    clientsocket, overpair = client[0]
    clientsocket.close()
    client[0] = (clientsocket, overpair)
    print(client.__repr__() + ' on blockingprocessheaders closed')
    #print('leave blockingprocessheaders')
