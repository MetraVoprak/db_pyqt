"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность
сетевых узлов. Аргументом функции является список, в котором каждый сетевой узел должен быть представлен
именем хоста или ip-адресом.В функции необходимо перебирать ip-адреса и проверять их доступность с
выводом соответствующего сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрессетевого
узла должен создаваться с помощью функции ip_address().
"""

from ipaddress import ip_address
from socket import gethostbyname
from subprocess import Popen, PIPE
import platform

import chardet


def host_ping(hosts_lst: list, need_print: bool = True) -> list:
    """
    Пингует каждый хост в данном списке и возвращает список с объектами ipaddress и статусом ping.
        :param hosts_lst: список хостов (список строк)
        :param need_print: включить/отключить встроенную печать
        :return: список кортежей, где первое значение является объектом ipaddress,
        а второе — логическим значением, представляющим доступность хоста.
    """
    checked_hosts = []
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # a = platform.system().lower()
    for host in hosts_lst:
        if type(host) is not str:
            raise ValueError(f'The passed object in the list must be of a str type. {type(host)} was given.')
        process = Popen(['ping', '-t2', param, '1', host], stdout=PIPE, stderr=PIPE)
        data, err = process.communicate()
        result = chardet.detect(data)
        result_decoded = data.decode(result['encoding'])
        is_reachable = False if "unreachable" in result_decoded else True
        ip = ip_address(gethostbyname(host))
        checked_hosts.append((ip, is_reachable))
        ip_str = str(ip)
        if need_print:
            print(f'Host {host if host == ip_str else (host + " (" + ip_str + ")")} is '
                  f'{"" if is_reachable else "un"}reachable')
    return checked_hosts


if __name__ == '__main__':
    hosts = ['google.com', 'ya.ru', '94.100.180.201', '87.240.132.72']
    host_ping(hosts)
    # Host google.com (216.58.210.142) is reachable
    # Host ya.ru (87.250.250.242) is reachable
    # Host 94.100.180.201 is reachable
    # Host 87.240.132.72 is reachable
