import requests
from datetime import datetime
root_host='http://127.0.0.1:8069'

def get_package_info(package_name):
    bandwidth = None
    ip_pool = None
    if "package" in package_name.lower() and "1" in package_name.lower():
        bandwidth = '20M/20M'
        ip_pool = 'PKG-1'
    elif "package" in package_name.lower() and "2" in package_name.lower():
        bandwidth = '30M/30M'
        ip_pool = 'PKG-2'
    elif "package" in package_name.lower() and "3" in package_name.lower():
        bandwidth = '40M/40M'
        ip_pool = 'PKG-3'
    elif "package" in package_name.lower() and "4" in package_name.lower():
        bandwidth = '50M/50M'
        ip_pool = 'PKG-4'

    else:
        bandwidth = None
        ip_pool = None
    return bandwidth,ip_pool


def create_radius_user(username,password,pool,enddate,customer_id):
    """
    Creating user for mime isp
    :param username: username for PPoE
    :param password: password for PPoE
    :param bandwidth: user bandwidth 10M/10M,30M/30M
    :param pool: ip pool name PKG-1, PKG-2, PKG-3, PKG-4 or Package name of ERP
    :param date: next expiry date
    :return: if successful then returns "success"
    """

    bandwidth,ip_pool=get_package_info(pool)
    if bandwidth!=None and ip_pool!=None:
        now = datetime.strptime(enddate,'%Y-%m-%d')
        date_time = now.strftime("%d %B %Y %H:%M")
        query=root_host+'/freeradius/create?username={}&password={}&bandwidth={}&pool={}&date={}&customer_id={}'
        r=requests.get(query.format(username, password,bandwidth,ip_pool,date_time,customer_id))
        return str(r.text)
    else:
        return 'error'

def update_billing_date(username,date):

    """
    Updating billing date

    :param username: username for PPoE
    :param date: next billing cycle
    :return: if successful then returns "success"
    """
    dateobject=datetime.strptime(date, '%Y-%m-%d')

    #dateobject2=dateobject+timedelta(days=30)

    ip_date=dateobject.strftime("%d %B %Y %H:%M")

    query = root_host + '/freeradius/update_expiry?username={}&date={}'
    r = requests.get(query.format(username, ip_date))
    return str(r.text)



def update_bandwidth(username,new_package,current_package):
    """
    Updating bandwidth of user

    :param username: username for PPoE
    :param bandwidth: user bandwidth 10M/10M,30M/30M
    :param new_package: new ip pool name PKG-1, PKG-2, PKG-3, PKG-4
    :param current_package: current ip pool name PKG-1, PKG-2, PKG-3, PKG-4
    :return: if successful then returns "success"
    """
    bandwidth,ip_pool=get_package_info(new_package)
    query = root_host + '/freeradius/update_bandwidth?username={}&bandwidth={}&update_package={}&current_package={}'
    r = requests.get(query.format(username, bandwidth, ip_pool, current_package))
    return str(r.text)

def update_expiry_bandwidth(username,expirydate,package):
    """
    Updating bandwidth and package of user

    :param username: username for PPoE
    :param bandwidth: user bandwidth 10M/10M,30M/30M
    :param expirydate: next billing cycle

    :return: if successful then returns "success"
    """
    dateobject = datetime.strptime(expirydate, '%Y-%m-%d')
    ip_date = dateobject.strftime("%d %B %Y %H:%M")

    print(username,expirydate,package)
    bandwidth,ip_pool=get_package_info(package)
    if bandwidth != None and ip_pool != None:
        query = root_host + '/freeradius/update_expiry_bandwidth?username={}&bandwidth={}&package={}&expirydate={}'
        r = requests.get(query.format(username, bandwidth, ip_pool, ip_date))
        return str(r.text)
    else:
        return 'error'