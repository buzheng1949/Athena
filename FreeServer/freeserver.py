#coding=utf-8
"""免密码登录远端服务器
Usage:
    freeserver <watch_server_ip>

Examples:
    freeserver xxxxxxx
"""
import pexpect
import os 
import getpass
from docopt import docopt
# 实现免密码登录方法
def login(fortresses_ip,user_name,password,watch_server_ip,command):
    child = pexpect.spawn('ssh -pxxx %s@%s'%(user_name,fortresses_ip))
    ret_login = child.expect(['%s@%s\'s password:'%(user_name,fortresses_ip),pexpect.TIMEOUT])
    if ret_login == 1:
        print ('login the remote server ip is timeout')
        return
    else:
        child.sendline(password)
        ret_password = child.expect(['This is a beta version. If you find bugs, please contact @Securit',pexpect.TIMEOUT])
        if ret_password == 1:
            print ('the password is wrong,please check the password')
            return
        else:
            child.sendline('p')
            ret_watch_server = child.expect([watch_server_ip,pexpect.TIMEOUT])
            if ret_watch_server != 0:
                print ('the password is correct,but the server ip maybe you have no perssion,please apply it')
                return
            else:
                child.sendline(watch_server_ip)
                child.expect('password')
                child.sendline(password)
                child.expect('Powered')
                if command is not None:
                    child.sendline(command)
                child.sendline('tailf web.log')
                child.interact()

def main():
    arguments = docopt(__doc__)
    watch_server_ip = arguments.get('<watch_server_ip>')
    user_name = 'your user name'
    password = 'your password'
    fortresses_ip = 'fortresses_ip'
    command = 'your command when your want success enter the ip server'
    login(fortresses_ip,user_name,password,watch_server_ip,command)

if __name__ == '__main__':
    main()