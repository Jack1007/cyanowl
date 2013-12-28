def exe(self, stanza, *args):
        body = "\n"
        if not args:
            body += "-exe {0}".format(self.exe.__doc__)
            return self._send_cmd_result(stanza, body)
        argv = [arg for arg in args if arg]
        if len(argv) < 2:
            body += "-exe {0}".format(self.exe.__doc__)
            return self._send_cmd_result(stanza, body)
        if argv[0] == 'tport':
            porthead = 'port,tcp'
        elif argv[0] == 'uport':
            porthead = 'port,udp'
        elif argv[0] == 'port':
            porthead = 'port,all'
        else:
            body += "-exe {0}".format(self.exe.__doc__)
            return self._send_cmd_result(stanza, body)
        ip = argv[1]
        sender = stanza.from_jid.bare().as_string()
        if len(argv) == 2:
            cmdmsg = porthead
        else:
            ports = argv[2:]
            strports = ','.join([str(p) for p in ports])
            cmdmsg = ','.join([porthead, strports])
        cmdmsg = ":".join(["258", ip, cmdmsg])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(12)
        try:
            sock.connect((MASTER_IP, MASTER_PORT))
            sock.send(cmdmsg)
            body = sock.recv(2048)
            sock.close()
        except:
            body = "Time out from CyanowlServer"
        #for p in ports:
        #    try:
        #        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #        sock.settimeout(1)
        #        sock.connect((ip, int(p)))
        #        body += "%s:%s listening\n" % (ip, p)
        #    except:
        #        body += "%s:%s down\n" % (ip, p)
        #    else:
        #        sock.close()
        finally:
            self._send_cmd_result(stanza, body)
