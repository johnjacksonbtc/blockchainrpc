import queue
import socket
import base64
import time
import inspect

def blockingreadheaders(client, nextjobs):

    # Start read network data blocking loop
    #print('enter blockingreadheaders(' + client.__repr__() + ', ' + nextjobs.__repr__() + ')')
    headers = b''
    headerslist = []
    print(client.__repr__() + ' on blockingreadheaders')
    clientsocket, overpair, clientaddress = client[0]
    overread, overwrite = overpair
    overread_i = 0
    overwrite_i = 0
    try:
        while True:
            #Calling any definition for each byte is a problem
            byte = b''
            if overread_i < len(overread):
                byte = overread[overread_i:overread_i + 1]
                overread_i += 1
            else:
                rawoverread = clientsocket.recv(1 << 20)
                overread = b''
                overread_i = 0
                if rawoverread:
                    overread = rawoverread
                if overread_i < len(overread):
                    byte = overread[overread_i:overread_i + 1]
                    overread_i += 1
            if byte:
                headers += byte
                if byte == b'\r':
                    byte = b''
                    if overread_i < len(overread):
                        byte = overread[overread_i:overread_i + 1]
                        overread_i += 1
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                    if byte:
                        headers += byte
                        if byte == b'\n':
                            headerslist += [headers]
                            headers = b''
                            byte = b''
                            if overread_i < len(overread):
                                byte = overread[overread_i:overread_i + 1]
                                overread_i += 1
                            else:
                                rawoverread = clientsocket.recv(1 << 20)
                                overread = b''
                                overread_i = 0
                                if rawoverread:
                                    overread = rawoverread
                                if overread_i < len(overread):
                                    byte = overread[overread_i:overread_i + 1]
                                    overread_i += 1
                            if byte:
                                headers += byte
                                if byte == b'\r':
                                    byte = b''
                                    if overread_i < len(overread):
                                        byte = overread[overread_i:overread_i + 1]
                                        overread_i += 1
                                    else:
                                        rawoverread = clientsocket.recv(1 << 20)
                                        overread = b''
                                        overread_i = 0
                                        if rawoverread:
                                            overread = rawoverread
                                        if overread_i < len(overread):
                                            byte = overread[overread_i:overread_i + 1]
                                            overread_i += 1
                                    if byte:
                                        headers += byte
                                        if byte == b'\n':
                                            headerslist += [headers]
                                            headers = b''
                                            nextjobqueue, nextjobpusher, futurejobs = nextjobs
                                            if not nextjobpusher.is_alive():
                                                try:
                                                    nextjobpusher.start()
                                                except RuntimeError:
                                                    pass
                                        
                                            # Blocking put
                                            client[0] = (clientsocket, (overread[overread_i:], overwrite[overwrite_i:]), clientaddress)
                                            nextjobqueue.put((client, headerslist, futurejobs))
                                            #print('return blockingreadheaders')
                                            return
            if not byte:
                break
    except ConnectionError:
        pass
    client[0] = (clientsocket, (overread[overread_i:], overwrite[overwrite_i:]), clientaddress)
    print(client.__repr__() + ' on blockingreadheaders closed, (headerslist, headers) = ' + (headerslist, headers).__repr__())
    clientsocket.close()
    #print('leave blockingreadheaders')

def blockingreaddata(client, length, backlinkqueue):
    #print('enter blockingreaddata(' + client.__repr__() + ', ' + length.__repr__() + ', ' + backlinkqueue.__repr__() + ')')
    status = b'not processed'
    contentmethod = 'unknown'
    contentlength = 0
    data = b''
    print(client.__repr__() + ' on blockingreaddata')
    clientsocket, overpair, clientaddress = client[0]
    overread, overwrite = overpair
    overread_i = 0
    overwrite_i = 0
    try:
        contentlength, contentmethod = length
    except ValueError:
        contentlength, = length
        contentmethod = None
    try:
        if contentmethod == None:
            if contentlength == None:
                while True:
                    datapart = b''
                    if overread_i < len(overread):
                        datapart = overread[overread_i:]
                        overread = b''
                        overread_i = 0
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            datapart = overread[overread_i:]
                            overread = b''
                            overread_i = 0
                    if datapart:
                        data += datapart
                    else:
                        status = b'received'
                        break
            else:
                while len(data) < length:
                    datapart = b''
                    if overread_i < len(overread):
                        datapart = overread[overread_i:overread_i + length - len(data)]
                        overread_i += length - len(data)
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            datapart = overread[overread_i:overread_i + length - len(data)]
                            overread_i += length - len(data)
                    if datapart:
                        data += datapart
                        if len(data) == length:
                            status = b'received'
                            break
                    else:
                        status = b'incomplete'
                        break
        elif contentmethod == b'chunked':
            while True:
                chunklength = 0
                expectchunklength = True
                while True:
                    byte = b''
                    if overread_i < len(overread):
                        byte = overread[overread_i:overread_i + 1]
                        overread_i += 1
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                    if byte:
                        if b'0'[0] <= byte[0] and byte[0] <= b'9'[0]:
                            if expectchunklength:
                                chunklength = chunklength * 16 + byte[0] - b'0'[0]
                        elif b'a'[0] <= byte[0] and byte[0] <= b'f'[0]:
                            if expectchunklength:
                                chunklength = chunklength * 16 + byte[0] - b'a'[0] + 10
                        elif b'A'[0] <= byte[0] and byte[0] <= b'F'[0]:
                            if expectchunklength:
                                chunklength = chunklength * 16 + byte[0] - b'A'[0] + 10
                        elif byte == '\r':
                            byte = b''
                            if overread_i < len(overread):
                                byte = overread[overread_i:overread_i + 1]
                                overread_i += 1
                            else:
                                rawoverread = clientsocket.recv(1 << 20)
                                overread = b''
                                overread_i = 0
                                if rawoverread:
                                    overread = rawoverread
                                if overread_i < len(overread):
                                    byte = overread[overread_i:overread_i + 1]
                                    overread_i += 1
                            if byte == b'\n':
                                break
                            elif not byte:
                                raise ConnectionError
                        elif expectchunklength:
                            expectchunklength = False
                    else:
                        raise ConnectionError
                if chunklength:
                    chunkdata = b''
                    while len(chunkdata) < chunklength:
                        chunkdatapart = b''
                        if overread_i < len(overread):
                            chunklength = overread[overread_i:overread_i + chunklength - len(chunkdata)]
                            overread_i += chunklength - len(chunkdata)
                        else:
                            rawoverread = clientsocket.recv(1 << 20)
                            overread = b''
                            overread_i = 0
                            if rawoverread:
                                overread = rawoverread
                            if overread_i < len(overread):
                                chunkdatapart = overread[overread_i:overread_i + chunklength - len(chunkdata)]
                                overread_i += chunklength - len(chunkdata)
                        if chunkdatapart:
                            chunkdata += chunkdatapart
                        else:
                            raise ConnectionError
                    byte = b''
                    if overread_i < len(overread):
                        byte = overread[overread_i:overread_i + 1]
                        overread_i += 1
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                    if byte != '\r':
                        raise ConnectionError
                    byte = b''
                    if overread_i < len(overread):
                        byte = overread[overread_i:overread_i + 1]
                        overread_i += 1
                    else:
                        rawoverread = clientsocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                    if byte != b'\n':
                        raise ConnectionError
                    data += chunkdata
                else:
                    while True:
                        byte = b''
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                        else:
                            rawoverread = clientsocket.recv(1 << 20)
                            overread = b''
                            overread_i = 0
                            if rawoverread:
                                overread = rawoverread
                            if overread_i < len(overread):
                                byte = overread[overread_i:overread_i + 1]
                                overread_i += 1
                        if byte == b'\r':
                            byte = b''
                            if overread_i < len(overread):
                                byte = overread[overread_i:overread_i + 1]
                                overread_i += 1
                            else:
                                rawoverread = clientsocket.recv(1 << 20)
                                overread = b''
                                overread_i = 0
                                if rawoverread:
                                    overread = rawoverread
                                if overread_i < len(overread):
                                    byte = overread[overread_i:overread_i + 1]
                                    overread_i += 1
                            if byte == b'\n':
                                byte = b''
                                if overread_i < len(overread):
                                    byte = overread[overread_i:overread_i + 1]
                                    overread_i += 1
                                else:
                                    rawoverread = clientsocket.recv(1 << 20)
                                    overread = b''
                                    overread_i = 0
                                    if rawoverread:
                                        overread = rawoverread
                                    if overread_i < len(overread):
                                        byte = overread[overread_i:overread_i + 1]
                                        overread_i += 1
                                if byte == b'\r':
                                    byte = b''
                                    if overread_i < len(overread):
                                        byte = overread[overread_i:overread_i + 1]
                                        overread_i += 1
                                    else:
                                        rawoverread = clientsocket.recv(1 << 20)
                                        overread = b''
                                        overread_i = 0
                                        if rawoverread:
                                            overread = rawoverread
                                        if overread_i < len(overread):
                                            byte = overread[overread_i:overread_i + 1]
                                            overread_i += 1
                                    if byte == b'\n':
                                        status = b'received'
                                        break
                        if not byte:
                            raise ConnectionError
                    break
    except ConnectionError:
        status = b'connection interrupted'
        print(client.__repr__() + ' on blockingreaddata closed')
        clientsocket.close()
    client[0] = (clientsocket, (overread[overread_i:], overwrite[overwrite_i:]), clientaddress)
    backlinkqueue.put((status, data))
    #print('leave blockingreaddata')

def blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue, recursion=0):
    #print('enter blockingrequestrpc(' + rpcsocketqueue.__repr__() + ', ' + ipportpair.__repr__() + ', ' + rpcauthpair.__repr__() + ', ' + jsondata.__repr__() + ', ' + backlinkqueue.__repr__() + ', ' + recursion.__repr__() + ')')
    family, ip, port = ipportpair
    connreuse = False
    serversocket = None
    overread = b''
    overread_i = 0
    overwrite = b''
    overwrite_i = 0
    server = [(serversocket, (overread[overread_i:], overwrite[overwrite_i:]))]
    #canreadnowqueue = None
    #readcompletedqueue = queue.Queue()
    try:
        #print('checkpoint ' + str(inspect.getframeinfo(inspect.currentframe()).lineno))
        try:
            #print('checkpoint ' + str(inspect.getframeinfo(inspect.currentframe()).lineno))
            #servertuple = rpcsocketqueue.get_nowait()
            #print('servertuple = ' + servertuple.__repr__())
            #try:
            #    server, canreadnowqueue = servertuple
            #except ValueError:
            #    server, = servertuple
            #server = servertuple
            serversocket, overpair = rpcsocketqueue.get_nowait()[0]
            overread, overwrite = overpair
            overread_i = 0
            overwrite_i = 0
            if serversocket == None:
                backlinkqueue.put((b'invalid socket received', b''))
                #print('checkpoint ' + str(inspect.getframeinfo(inspect.currentframe()).lineno))
                return
            connreuse = True
        except queue.Empty:
            #print('checkpoint ' + str(inspect.getframeinfo(inspect.currentframe()).lineno))
            connreuse = False
            serversocket = socket.socket(family, socket.SOCK_STREAM)
            serversocket.connect((ip, port))
            overread = b''
            overread_i = 0
            overwrite = b''
            overwrite_i = 0
        username, password = rpcauthpair
        jsondatalen = len(jsondata)
        status = b'not processed'
        data = b''
        senddata = b''
        senddata += b'POST / HTTP/1.1\r\n'
        senddata += b'Host: ' + ip.encode() + b':' + str(port).encode() + b'\r\n'
        senddata += b'Authorization: Basic ' + base64.b64encode(username.encode() + b':' + password.encode()) + b'\r\n'
        senddata += b'User-Agent: blockchainrpc/0.0\r\n'
        senddata += b'Connection: Keep-Alive\r\n'
        senddata += b'Accept: */*\r\n'
        senddata += b'Content-Type: text/plain\r\n'
        senddata += b'Content-Length: ' + str(jsondatalen).encode() + b'\r\n'
        senddata += b'\r\n'
        senddata += jsondata
        overwrite_do = (b'POST / HTTP/1.1\r\nHost: ' + ip.encode() + b':' + str(port).encode() + b'\r\n')[0:61 + (3 & jsondatalen)]
        try:
            if len(overwrite):
                overwritematch_senddata = b''
                if (len(senddata) + len(overwrite_do)) < len(overwrite):
                    overwritematch_senddata = (senddata + overwrite_do)[0:len(senddata) + len(overwrite_do)]
                else:
                    overwritematch_senddata = (senddata + overwrite_do)[0:len(overwrite)]
                if overwritematch_senddata == overwrite[0:len(overwritematch_senddata)]:
                    overwrite_i += len(overwritematch_senddata)
                    if (senddata + overwrite_do)[len(overwritematch_senddata):]:
                        serversocket.sendall((senddata + overwrite_do)[len(overwritematch_senddata):])
                        overwrite = overwrite + overwrite_do
                        overwrite_do = b''
                else:
                    print(server.__repr__() + ' on blockingsendresponse overwrite failure, ' + overwritematch_senddata.__repr__() + ' expected, ' + overwrite[0:len(overwritematch_senddata)].__repr__() + ' written early')
                    raise ConnectionError
            else:
                serversocket.sendall(senddata + overwrite_do)
                overwrite = overwrite_do
                overwrite_i = 0
                overwrite_do = b''
        except OSError:
            server[0] = (serversocket, (overread[overread_i:], overwrite[overwrite_i:]))
            print('blockingrequestrpc detected OSError on server.sendall(senddata), server = ' + server.__repr__() + ' retrying recursively')
            #time.sleep(recursion+1)
            blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue, recursion+1)
            return
        headers = b''
        headerslist = []
        #print('canreadnowqueue ' + canreadnowqueue.__repr__() + 'waiting')
        #if canreadnowqueue and canreadnowqueue.get() != b'ok':
        #    if recursion == 0:
        #        print('blockingrequestrpc detected http pipelining failure on ' + str(ip) + ':' + str(port) + ' while processing ' + str(jsondata) + ', connreuse: ' + str(connreuse) + ', retrying recursively\r\n')
        #    if server:
        #        server.close()
        #    time.sleep(recursion+1)
        #    blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue, recursion+1)
        #    return
        #print('canreadnowqueue ' + canreadnowqueue.__repr__() + ' wait completed')
        #rpcsocketqueue.put((server, readcompletedqueue))
        #rpcsocketqueue.put(server)
        #print('(server, readcompletedqueue) ' + (server, readcompletedqueue).__repr__() + ' pushed into socket queue')
        while True:
            byte = b''
            if overread_i < len(overread):
                byte = overread[overread_i:overread_i + 1]
                overread_i += 1
            else:
                rawoverread = serversocket.recv(1 << 20)
                overread = b''
                overread_i = 0
                if rawoverread:
                    overread = rawoverread
                if overread_i < len(overread):
                    byte = overread[overread_i:overread_i + 1]
                    overread_i += 1
            if byte:
                headers += byte
                if byte == b'\r':
                    byte = b''
                    if overread_i < len(overread):
                        byte = overread[overread_i:overread_i + 1]
                        overread_i += 1
                    else:
                        rawoverread = serversocket.recv(1 << 20)
                        overread = b''
                        overread_i = 0
                        if rawoverread:
                            overread = rawoverread
                        if overread_i < len(overread):
                            byte = overread[overread_i:overread_i + 1]
                            overread_i += 1
                    if byte:
                        headers += byte
                        if byte == b'\n':
                            headerslist += [headers]
                            headers = b''
                            byte = b''
                            if overread_i < len(overread):
                                byte = overread[overread_i:overread_i + 1]
                                overread_i += 1
                            else:
                                rawoverread = serversocket.recv(1 << 20)
                                overread = b''
                                overread_i = 0
                                if rawoverread:
                                    overread = rawoverread
                                if overread_i < len(overread):
                                    byte = overread[overread_i:overread_i + 1]
                                    overread_i += 1
                            if byte:
                                headers += byte
                                if byte == b'\r':
                                    byte = b''
                                    if overread_i < len(overread):
                                        byte = overread[overread_i:overread_i + 1]
                                        overread_i += 1
                                    else:
                                        rawoverread = serversocket.recv(1 << 20)
                                        overread = b''
                                        overread_i = 0
                                        if rawoverread:
                                            overread = rawoverread
                                        if overread_i < len(overread):
                                            byte = overread[overread_i:overread_i + 1]
                                            overread_i += 1
                                    if byte:
                                        headers += byte
                                        if byte == b'\n':
                                            headerslist += [headers]
                                            headers = b''
                                            i = 0
                                            headerscount = len(headerslist)
                                            contentlength = 0
                                            status = b'no data'
                                            while i < headerscount:
                                                headers = headerslist[i]
                                                headerkey = b''
                                                headerslen = len(headers)
                                                j = 0
                                                while j < headerslen:
                                                    if headers[j:j+1] != b':':
                                                        if b'a'[0] <= headers[j] and headers[j] <= b'z'[0]:
                                                            headerkey += bytes([headers[j] - b'a'[0] + b'A'[0]])
                                                        else:
                                                            headerkey += headers[j:j+1]
                                                    else:
                                                        break
                                                    j += 1
                                                if headerkey == b'CONTENT-LENGTH':
                                                    j += 1
                                                    while j < headerslen:
                                                        if b'0'[0] <= headers[j] and headers[j] <= b'9'[0]:
                                                            contentlength = contentlength * 10 + headers[j] - b'0'[0]
                                                        j += 1
                                                    break
                                                i += 1
                                            if contentlength:
                                                data = b''
                                                while len(data) < contentlength:
                                                    col52data = b''
                                                    if overread_i < len(overread):
                                                        col52data = overread[overread_i:overread_i + contentlength - len(data)]
                                                        overread_i += contentlength - len(data)
                                                    else:
                                                        rawoverread = serversocket.recv(1 << 20)
                                                        overread = b''
                                                        overread_i = 0
                                                        if rawoverread:
                                                            overread = rawoverread
                                                        if overread_i < len(overread):
                                                            col52data = overread[overread_i:overread_i + contentlength - len(data)]
                                                            overread_i += contentlength - len(data)
                                                    if col52data:
                                                        data += col52data
                                                        if len(data) == contentlength:
                                                            status = b'received'
                                                            #readcompletedqueue.put(b'ok')
                                                            #print('readcompletedqueue ' + readcompletedqueue.__repr__() + ' unlocked with ok')
                                                            server[0] = (serversocket, (overread[overread_i:], overwrite[overwrite_i:]))
                                                            rpcsocketqueue.put(server)
                                                            backlinkqueue.put((status, data))
                                                            if recursion:
                                                                print('blockingrequestrpc detected failure on ' + str(ip) + ':' + str(port) + ' while processing (first 1024 bytes) ' + str(jsondata[0:1024]) + ', completed on ' + str(recursion+1) + '. try\r\n')
                                                            return
                                                    else:
                                                        status = b'incomplete response, got ' + str(len(data)).encode() + b' of ' + str(contentlength).encode() + b' bytes'
                                                        break
                                            break
            if not byte:
                break
    except ConnectionError:
        if recursion == 0:
            print('blockingrequestrpc detected ConnectionError on ' + str(ip) + ':' + str(port) + ' while processing (first 1024 bytes) ' + str(jsondata[0:1024]) + ', connreuse: ' + str(connreuse) + ', retrying recursively\r\n')
        if serversocket:
            serversocket.close()
        server[0] = (serversocket, (overread[overread_i:], overwrite[overwrite_i:]))
        #readcompletedqueue.put(b'failed')
        #print('readcompletedqueue ' + readcompletedqueue.__repr__() + 'unlocked with failed')
        #time.sleep(recursion+1)
        #print('recurse blockingrequestrpc')
        blockingrequestrpc(rpcsocketqueue, ipportpair, rpcauthpair, jsondata, backlinkqueue, recursion+1)
        return
    #readcompletedqueue.put(b'failed')
    #print('readcompletedqueue ' + readcompletedqueue.__repr__() + 'unlocked with failed')
    if serversocket:
        serversocket.close()
    server[0] = (serversocket, (overread[overread_i:], overwrite[overwrite_i:]))
    backlinkqueue.put((status, data))
    #print('leave blockingrequestrpc')
    
def blockingsendresponse(client, data, reuseconnection, backlinkqueue):
    #print('enter blockingsendresponse(' + client.__repr__() + ', ' + data.__repr__() + ', ' + reuseconnection.__repr__() + ', ' + backlinkqueue.__repr__() + ')')
    print(client.__repr__() + ' on blockingsendresponse')
    clientsocket, overpair, clientaddress = client[0]
    overread, overwrite = overpair
    overread_i = 0
    overwrite_i = 0
    try:
        if len(overwrite):
            overwritematch_data = b''
            if len(data) < len(overwrite):
                overwritematch_data = data[0:len(data)]
            else:
                overwritematch_data = data[0:len(overwrite)]
            if overwritematch_data == overwrite[0:len(overwritematch_data)]:
                overwrite_i += len(overwritematch_data)
                if data[len(overwritematch_data):]:
                    clientsocket.sendall(data[len(overwritematch_data):])
            else:
                print(client.__repr__() + ' on blockingsendresponse overwrite failure, ' + overwritematch_data.__repr__() + ' expected, ' + overwrite[0:len(overwritematch_data)].__repr__() + ' written early')
                raise ConnectionError
        else:
            clientsocket.sendall(data)
    except ConnectionError:
        reuseconnection = False
    client[0] = (clientsocket, (overread[overread_i:], overwrite[overwrite_i:]), clientaddress)
    if reuseconnection:
        backlinkqueue.put(client)
        print(client.__repr__() + ' on blockingsendresponse repurposed')
    else:
        print(client.__repr__() + ' on blockingsendresponse closed')
        clientsocket.close()
    #print('leave blockingsendresponse')

def blockingacceptloop(addressfamily, serveraddress, port, backlinkqueue):
    sock = socket.socket(addressfamily, socket.SOCK_STREAM)
    sock.bind((serveraddress, port))
    sock.listen()
    print('Server is ready to accept connections on ' + serveraddress + ' port ' + str(port))
    while True:
        client, clientaddress = sock.accept()
        overread = b''
        overwrite = b''
        print(client.__repr__() + ' on accept loop')
##        byte = None
##        try:
##            byte = client.recv(1)
##        except ConnectionError:
##            pass
##        if byte:
##            overread += byte
##            backlinkqueue.put([(client, (overread, overwrite), clientaddress)])
##        else:
##            print(client.__repr__() + ' on accept loop closed')
##            client.close()
        backlinkqueue.put([(client, (overread, overwrite), clientaddress)])
        
