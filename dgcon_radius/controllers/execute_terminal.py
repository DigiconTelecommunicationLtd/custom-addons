# -*- coding: utf-8 -*-

#depepdency: 'sqlalchemy','paramiko',
import paramiko
import sys

# sample "echo user-name=sm.tanvir | radclient -x 103.117.192.4:3799 disconnect test"

#echo user-name=cust-30 | radclient -x 172.16.1.2:3799 disconnect mime
#echo user-name=cust-30 | radclient -x 172.16.1.18:3799 disconnect mime

#Under UTC PoP:
#update radreply set value = '30M/30M' where  username = 'cust-30' AND attribute = "Mikrotik-Rate-Limit";

#echo user-name=cust-30 | radclient -x 172.16.1.77:3799 disconnect mime
#echo user-name=cust-30 | radclient -x 172.16.1.62:3799 disconnect mime

#Under Mirpur PoP:
#update radreply set value = '30M/30M' where  username = 'cust-30' AND attribute = "Mikrotik-Rate-Limit";

#echo user-name=cust-30 | radclient -x 172.16.1.42:3799 disconnect mime
#echo user-name=cust-30 | radclient -x 172.16.1.61:3799 disconnect mime

def disconnect(customer_id):
    """
    Disconnects the user from pop and updates the bandwidth

    Parameters
    ----------
    customer_id : str
        customer user name

    Returns
    -------
        None
    """
    PASS = 'mime'
    hostname = '103.117.192.79'
    port = 22
    username = 'root'
    password = 'M!M3-R@d!u5'
    #command = 'echo user-name={} | radclient -x {}:3799 disconnect '+PASS

    command1 = 'echo user-name={} | radclient -x 172.16.1.2:3799 disconnect ' + PASS+';'
    command2 = 'echo user-name={} | radclient -x 172.16.1.18:3799 disconnect ' + PASS + ';'
    command3 = 'echo user-name={} | radclient -x 172.16.1.77:3799 disconnect ' + PASS + ';'
    command4 = 'echo user-name={} | radclient -x 172.16.1.62:3799 disconnect ' + PASS + ';'
    command5 = 'echo user-name={} | radclient -x 172.16.1.42:3799 disconnect ' + PASS + ';'
    command6 = 'echo user-name={} | radclient -x 172.16.1.61:3799 disconnect ' + PASS + ';'

    client = paramiko.Transport((hostname, port))
    client.connect(username=username, password=password)
    command = command1.format(customer_id) + \
              command2.format(customer_id) + \
              command3.format(customer_id) + \
              command4.format(customer_id) + \
              command5.format(customer_id) + \
              command6.format(customer_id)


    session = client.open_channel(kind='session')
    #start all the commands
    session.exec_command(command)

    #stdout_data = []
    #stderr_data = []
    #nbytes = 4096
    #session.exec_command(command)

    # while True:
    #     if session.recv_ready():
    #         stdout_data.append(session.recv(nbytes))
    #     if session.recv_stderr_ready():
    #         stderr_data.append(session.recv_stderr(nbytes))
    #     if session.exit_status_ready():
    #         break
    #
    # print('exit status: ', session.recv_exit_status())
    # print(''.join(stdout_data))
    # print(''.join(stderr_data))

    session.close()
    client.close()