import requests

root_host='http://127.0.0.1:8069'

def create_user(username,password,bandwidth,pool,date):
    """
    Creating user for mime isp
    :param username: username for PPoE
    :param password: password for PPoE
    :param bandwidth: user bandwidth 10M/10M,30M/30M
    :param pool: ip pool name PKG-1, PKG-2, PKG-3, PKG-4
    :param date: next expiry date
    :return: if successful then returns "success"
    """

    query=root_host+'/freeradius/create?username={}&password={}&bandwidth={}&pool={}&date={}'
    r=requests.get(query.format(username, password,bandwidth,pool,date))
    return str(r.text)


def update_bandwidth(username,bandwidth,new_package,current_package):
    """
    Updating bandwidth of user

    :param username: username for PPoE
    :param bandwidth: user bandwidth 10M/10M,30M/30M
    :param new_package: new ip pool name PKG-1, PKG-2, PKG-3, PKG-4
    :param current_package: current ip pool name PKG-1, PKG-2, PKG-3, PKG-4
    :return: if successful then returns "success"
    """
    query = root_host + '/freeradius/update_bandwidth?username={}&bandwidth={}&update_package={}&current_package={}'
    r = requests.get(query.format(username, bandwidth, new_package, current_package))
    return str(r.text)


def update_billing_date(username,date):
    """
    Updating billing date

    :param username: username for PPoE
    :param date: next billing cycle
    :return: if successful then returns "success"
    """
    query = root_host + '/freeradius/update_expiry?username={}&date={}'
    r = requests.get(query.format(username, date))
    return str(r.text)


