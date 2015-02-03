import distribute.common as com
import logging

logging.basicConfig(level=logging.DEBUG, filename='log')

hosts=['10.0.34.219',]
user_name='wgz'
pwd='111'
cmds=['ls /', 'ls /usr']

com.distributed_ssh_cmds(hosts, user_name, pwd, cmds)

