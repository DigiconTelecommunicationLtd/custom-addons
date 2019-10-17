# -*- coding: utf-8 -*-

# depepdency: 'sqlalchemy','paramiko',

import traceback
from sqlalchemy import create_engine
from .execute_terminal import disconnect
from .radius_cred import *
# creadiendial to connect to the database
#database_cred = 'mysql://root:my5ql-137967@103.117.192.79:3306/radius'

CREATE_USER = "INSERT INTO radcheck ( id , UserName , Attribute , op , Value ) VALUES ( NULL , '{}', 'Cleartext-Password', ':=', '{}')"
CREATE_EXPIRY = "INSERT INTO radcheck ( id , UserName , Attribute , op , Value ) VALUES ( NULL , '{}', 'Expiration', ':=', '{}')"

CREATE_BANDWITDH = "INSERT INTO radreply (username, attribute, op, value) VALUES ('{}', 'Mikrotik-Rate-Limit', '==', '{}')"
CREATE_IP_POOL = "INSERT INTO radreply ( id , UserName , Attribute , op , Value ) VALUES ( NULL , '{}', 'Framed-Pool', '==' , '{}')"

CREATE_REAL_IP_POOL = "INSERT INTO radreply ( id , UserName , Attribute , op , Value ) VALUES ( NULL , '{}', 'Real-IP', '==' , '{}')"

UPDATE_EXPIRY = "UPDATE radcheck set value = '{}' where  username = '{}' AND attribute = 'Expiration'"
DISCONNECT = "UPDATE radreply SET value = '1k/1k' where username = '{}'"
UPDATE_BANDWIDTH = "UPDATE radreply SET value = '{}' where username = '{}' AND attribute = 'Mikrotik-Rate-Limit'"
UPDATE_POOL = "UPDATE radreply SET Value = '{}' where username = '{}' AND attribute = 'Framed-Pool' AND op = '=='"


PKG1='PKG-1'
PKG2='PKG-2'
PKG3='PKG-3'
PKG4='PKG-4'

def execute(query):
    """
    Parameters
    ----------
    query: str
        the query string for the database

    Returns
    -------
    bool,str:
        returns bool and string in tuple format. bool is true for success and false for failure

    """
    engine = create_engine(database_cred)

    with engine.connect() as con:
        try:
            rs = con.execute(query)
            return True, rs
        except Exception as e:
            print(traceback.print_exc())
            return False, e.__class__.__name__


def create_connection_realip(username, password, bandwidth, real_ip, date):
    """
    Function responsible for connecting and creating the user.
    This performs four database write operation.
        1. Insert user info in radcheck
        2. Insert billing info in radcheck
        3. Insert bandwidth info in radreply
        4. Insert IP POOL data in radreply
    Parameters
    ----------
    username : str
        username for the client. This will be needed for PPoE access

    password: str
        password for the client. This also will be needed for PPoE access

    bandwidth: str
        assign bandwidth for the client. Format 10M/20M

    pool: str
        IP pool for the client.

    date: str
        Billing cycle

    Returns
    -------
    str
        returns 'success' if successful, otherwise returns debug data.
    """

    sum = 'START TRANSACTION;'+CREATE_USER.format(username, password)+';'\
          +CREATE_EXPIRY.format(username, date)+';'\
          +CREATE_BANDWITDH.format(username, bandwidth)+';'\
          +CREATE_REAL_IP_POOL.format(username, real_ip)+';'\
          +'COMMIT;'

    data,status= execute(sum)

    if status:
        return 'success'
    else:
        return 'create user ' + str(status) + ' ' + str(data)

    # status1, data1 = execute(CREATE_USER.format(username, password))
    # status2, data2 = execute(CREATE_EXPIRY.format(username, date))
    # status3, data3 = execute(CREATE_BANDWITDH.format(username, bandwidth))
    # status4, data4 = execute(CREATE_IP_POOL.format(username, pool))


def create_connection(username, password, bandwidth, pool, date):
    """
    Function responsible for connecting and creating the user.
    This performs four database write operation.
        1. Insert user info in radcheck
        2. Insert billing info in radcheck
        3. Insert bandwidth info in radreply
        4. Insert IP POOL data in radreply
    Parameters
    ----------
    username : str
        username for the client. This will be needed for PPoE access

    password: str
        password for the client. This also will be needed for PPoE access

    bandwidth: str
        assign bandwidth for the client. Format 10M/20M

    pool: str
        IP pool for the client.

    date: str
        Billing cycle

    Returns
    -------
    str
        returns 'success' if successful, otherwise returns debug data.
    """

    sum = 'START TRANSACTION;'+CREATE_USER.format(username, password)+';'\
          +CREATE_EXPIRY.format(username, date)+';'\
          +CREATE_BANDWITDH.format(username, bandwidth)+';'\
          +CREATE_IP_POOL.format(username, pool)+';'\
          +'COMMIT;'

    data,status= execute(sum)

    if status:
        return 'success'
    else:
        return 'create user ' + str(status) + ' ' + str(data)

    # status1, data1 = execute(CREATE_USER.format(username, password))
    # status2, data2 = execute(CREATE_EXPIRY.format(username, date))
    # status3, data3 = execute(CREATE_BANDWITDH.format(username, bandwidth))
    # status4, data4 = execute(CREATE_IP_POOL.format(username, pool))


def update_connection(username, bandwidth, update_package):

    """
    Function responsible for connecting and updating bandwidth.
    This performs two database write operation and one server.
        1. Update bandwidth info in radreply
        2. Update IP POOL data in radreply
        3. Disconnects the user to ensure user bandwidth is updated
    Parameters
    ----------
    username : str
        username for the client. This will be needed for PPoE access

    bandwidth: str
        assign bandwidth for the client. Format 10M/10M

    update_package: str
        name of the updated package

    Returns
    -------
    str
        returns 'success' if successful, otherwise returns debug data.
    """

    sum = 'START TRANSACTION;'+UPDATE_BANDWIDTH.format(bandwidth, username)+';'+UPDATE_POOL.format(update_package, username)+';'+'COMMIT;'
    status, data = execute(sum)


    disconnect(username)
    if status:
        return 'success'
    else:
        return str(status) + ' ' + str(data)


def update_expiry(username, date):
    """
    Updates expiry date

    Parameters
    ----------
    username : str
        username for the client for PPoE
    date : str
         Billing cycle

    Returns
    -------
    str
        returns 'success' if successful, otherwise returns debug data.
    """

    status, data = execute(UPDATE_EXPIRY.format(date, username))

    if status:
        return 'success'
    else:
        return str(status) + ' ' + str(data)



def update_bandwitdh_expiry(username,expirydate,bandwidth, package):
    """
       Updates expiry and bandwitdh

       Parameters
       ----------
       username : str
           username for the client for PPoE

        bandwidth: str
            assign bandwidth for the client. Format 10M/10M

       expirydate : str
            Billing cycle

       package: str
            name of the updated package
       Returns
       -------
       str
           returns 'success' if successful, otherwise returns debug data.
       """
    sum='START TRANSACTION;'+\
        UPDATE_BANDWIDTH.format(bandwidth, username)+';'+\
        UPDATE_POOL.format(package, username)+';'+ \
        UPDATE_EXPIRY.format(expirydate, username)+';'+ \
        'COMMIT;'

    status, data = execute(sum)
    if status:
        return 'success'
    else:
        return str(status) + ' ' + str(data)
