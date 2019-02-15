import connections, socks
from keys import read
from sys import exit
import json
import requests

port = 8150

def convert_ip_port(ip, some_port):
    """
    Get ip and port, but extract port from ip if ip was as ip:port
    :param ip:
    :param some_port: default port
    :return: (ip, port)
    """
    if ':' in ip:
        ip, some_port = ip.split(':')
    return ip, some_port
    
    
key, public_key_readable, private_key_readable, public_key_hashed, address = read()

wallets = []

 """
Connect to API-Server and get WalletServer status information, 
sort available Servers for least used and return the sorted list
"""
try:

    rep = requests.get("http://api.bismuth.live/servers/wallet/legacy.json")
    if rep.status_code == 200:
        wallets = rep.json()
        #print(wallets)
except Exception as e:
    print("Error {} getting Server list from API".format(e))


if wallets:
    # We have a server list, order by load
    sorted_wallets = sorted([wallet for wallet in wallets if wallet['active']], key=lambda k: (k['clients']+1)/(k['total_slots']+2))
    #print(sorted_wallets)
    """
    # try to connect in sequence, keep the first one ok.
    for wallet in sorted_wallets:
        print(wallet)
        ipport = "{}:{}".format(wallet['ip'], wallet['port'])
        print(ipport)
        if lwbench.connectible(ipport):
            return [ipport]
    """
    if sorted_wallets:
        light_ip = ["{}:{}".format(wallet['ip'], wallet['port']) for wallet in sorted_wallets]

else:
    exit("Server or API-Server unreachable, try again in few minutes or ask for help in #support in https://discordapp.com/channels/348020833194868751/392572196855480320")
     

"""
Connect to WalletServer, send bismuth-API request and stop trying after answer
"""     
keep_trying = True
while keep_trying:
    for ip in light_ip:
        try:
            ip, local_port = convert_ip_port(ip, port)
            s = socks.socksocket()
            s.settimeout(10)
            s.connect((ip, int(local_port)))
            connections.send (s, "balanceget", 10)
            connections.send (s, address, 10)
            balanceget_result = connections.receive (s, 10)
            keep_trying = False
            break
        except Exception as e:
            print("Status: Cannot connect to {}:{}".format(ip, local_port))
            time.sleep(1)





print ("Address balance: {}".format (balanceget_result[0]))
print ("Address credit: {}".format (balanceget_result[1]))
print ("Address debit: {}".format (balanceget_result[2]))
print ("Address fees: {}".format (balanceget_result[3]))
print ("Address rewards: {}".format (balanceget_result[4]))
print ("Address balance without mempool: {}".format (balanceget_result[5]))
exit("Done!")


