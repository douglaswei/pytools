
# coding:utf-8 

import pexpect

def ssh_cmd(host, user_name, pwd, cmd):
    status = -1
    ssh = pexpect.spawn('ssh %s@%s "%s"' % (user_name, host, cmd))
    try: 
        remote_status = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=5) 
        if remote_status == 0 : 
            ssh.sendline(pwd) 
        elif remote_status == 1: 
            ssh.sendline('yes') 
            ssh.expect('password: ') 
            ssh.sendline(passwd) 
            ssh.sendline(cmd) 
        remote_output = ssh.read() 
        status = 0 
    except pexpect.EOF, e: 
        remote_output = "EOF:" + str(e)
        ssh.close() 
        status = -1 
    except pexpect.TIMEOUT, e: 
        remote_output =  "TIMEOUT" + str(e)
        ssh.close() 
        status = -2 
    return status, remote_output

