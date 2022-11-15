"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from ipaddress import ip_network

from task_1 import host_ping


def host_range_ping(host_range: str, need_print: bool = True) -> list:
    """
    Пингует хосты в заданном диапазоне.
        :param host_range: диапазон IP-адресов
        :param need_print: включить/отключить встроенную печать
        :return: список кортежей, где первое значение является объектом ipaddress,
        а второе — логическим значением, представляющим доступность хоста.
    """
    hosts = []
    if '/' in host_range:
        hosts = [str(ip) for ip in ip_network(host_range)]
    elif '-' in host_range:
        start_ip, end = [item.strip() for item in host_range.split('-')]
        if '.' in end:
            end = end.rsplit('.', 1)[-1]
        start = int(start_ip.rsplit('.', 1)[-1])
        end = int(end)
        start_ip = start_ip.rsplit(".", 1)[0]
        hosts = [f'{start_ip}.{i}' for i in range(start, end + 1)]
    else:
        hosts.append(host_range)
    return host_ping(hosts, need_print)


if __name__ == '__main__':
    host_range = '87.240.132.0/23'
    host_range_ping(host_range)
    print('=' * 20)
    host_range = '192.168.178.0-7'
    host_range_ping(host_range)
    print('=' * 20)
    host_range = '192.168.178.0-192.168.178.7'
    host_range_ping(host_range)

