#!/usr/bin/env python
#-*-coding:utf-8 -*-
# 这个文件里定义了各个模块需要的字典值
tcpstate = {"ERROR_STATUS"   :'00',
            "TCP_ESTABLISHED":'01',
            "TCP_SYN_SENT"   :'02',
            "TCP_SYN_RECV"   :'03',
            "TCP_FIN_WAIT1"  :'04',
            "TCP_FIN_WAIT2"  :'05',
            "TCP_TIME_WAIT"  :'06',
            "TCP_CLOSE"      :'07',
            "TCP_CLOSE_WAIT" :'08',
            "TCP_LAST_ACK"   :'09',
            "TCP_LISTEN"     :'0A',
            "TCP_CLOSING"    :'0B', 
	    "UNKNOWN"        :'0C' }

order = {'port' : ['port'],
         'restart':[],
	 'osinfo':[],
	 'info':[],
	 'serverinfo': [],
	 'diskinfo':[],
	 'network':[],
	 'logindetail':[],
	 'process':[],
	 'close': [],
	 'shutdown':[]}

#port{tcp,udp}
#restart:{java,nginx,memcached,redis,zookeeper}
#osinfo:{kernel,release,gcc,uptime,load,processcount,hostname}
#info:{java-version,memcached-version,zookeeper-version,redis-versin,php-version,nginx,apache}
      #javae-rsion{javarelease,java-intall-dir}
      #memcached-version{memcachedrelease,memcached-install-dir,memcached-start-args,memcached-process-count,master-slave,startuser}
      #redis-version{redisrelease,redis-install-dir,redis-start-args,redis-process-count,master-slave,startuser}
      #zookeeper-version{zookeeperrelease,zookeeper-install-dir,zookeeper-start-args,zookeeper-process-count,startuser}
      #php-version{phprelease,php-install-dir,php-process-count,php-mod,startuser}
      #nginx{nginxrelease,nginx-install-dir,nginx-process-count,nginx-domains,startuser}
      #apache{httpdrelease,httpd-install-dir,httpd-process-count,httpd-vhosts,startuser}
#serverinfo{sn,model,bioscpufeq,cpucores,memory,raid,diskcount,networkcards,card-ip,card-workingmode,}
#diskinfo{rootpartition,swap,export,shm,tmp}
#network{tcpstatecount,port-foreginerip-count}
#logindetail{currentlogingname,time,user}
#process{connections,resmem,cpu-use,fdcount}
