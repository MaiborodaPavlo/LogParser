import socket
import re
import json
import time
import bisect

from collections import namedtuple, defaultdict


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
FILE_NAME = 'otrs_error.log'


def parse_request(b_data):
    """Разбираем полученный запрос
    Возвращается None если запрос не по шаблону
    В противном случае namedtuple('Request_data', 'h m s error')"""

    data = b_data.decode("utf-8")
    # HH[:MM[:SS]]-<some_string>
    pattern = r'(?P<h>^\d{2}):?(?P<m>\d{2})?:?(?P<s>\d{2})?-(?P<error>[\w:]*)'
    match = re.match(pattern, data)

    Request_data = namedtuple('Request_data', 'h m s error')

    return Request_data(*match.groups()) if match is not None else match


def search_errors_re(req_data):
    """Поиск нужных строк с помощью регулярного выражения"""

    pattern = r'(\[.*{}:{}:{}.*\]\[.*\]\[.*{}.*\]\[.*\] .*)'\
        .format(req_data.h,
                f'{req_data.m if req_data.m is not None else ".*"}',
                f'{req_data.s if req_data.s is not None else ".*"}',
                req_data.error)

    with open(FILE_NAME, 'r') as log:
        return re.findall(pattern, log.read())


# Дополнительное задание

def parse_log(req_data):
    """Парсинг лога с регулярного выражения
    Возвращается defaultdict, где
    ключи - время
    значения - строки лога"""

    pattern = r'^\[.*{}.*\]\[.*\]\[.*{}.*\]\[.*\] .*$'\
        .format('(?P<time>\d{2}:\d{2}:\d{2})',
                req_data.error)

    time_grouped_dict = defaultdict(list)

    with open(FILE_NAME, 'r') as log:

        for line in log:
            match = re.search(pattern, line)

            if match:
                time_grouped_dict[match.group('time')].append(line)

    return time_grouped_dict


def timeit(func):
    """Декоратор для подсчета времени выполнения поиска"""

    def wrapped(*args):
        s_time = time.time()
        result = func(*args)
        print(f'{func.__name__}: {(time.time() - s_time) * 1000} ms')
        return result
    return wrapped


@timeit
def search_errors(time_grouped_dict, req_data):
    """Линейный поиск"""

    if req_data.s is not None:
        return time_grouped_dict[f'{req_data.h}:{req_data.m}:{req_data.s}']

    else:
        start, end = get_time_range(req_data.h, req_data.m)

        result = []

        for key, val in time_grouped_dict.items():
            if is_time_in_range(start, end, key):
                result.extend(val)

        return result


@timeit
def search_errors_binary(time_grouped_dict, req_data):
    """Поиск, методом деления пополам,
    реализован с помощью модуля bisect.
    Сортируем данные и находим в них нужный нам отрезок"""

    if req_data.s is not None:
        return time_grouped_dict[f'{req_data.h}:{req_data.m}:{req_data.s}']

    else:
        start, end = get_time_range(req_data.h, req_data.m)

        result = []

        sorted_keys = sorted(time_grouped_dict.keys())

        idx_start = bisect.bisect_left(sorted_keys, start)
        idx_end = bisect.bisect_right(sorted_keys, end)

        for key in sorted_keys[idx_start:idx_end]:
            result.extend(time_grouped_dict[key])

        return result


# Вспомогательные функции

def is_time_in_range(start, end, x):
    """Проверка на попадание во временной интервал"""

    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def get_time_range(h, m):
    """Возвращается tuple с временным интервалом"""

    return (f'{h}:{m if m is not None else "00"}:00',
            f'{h}:{m if m is not None else "59"}:59')


# main

def create_sock(ip=TCP_IP, port=TCP_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen()

    return sock


def accept_client_conn(sock):
    client_sock, client_addr = sock.accept()
    print(f'Адрес клиента: {client_addr}')
    print('-' * 30)

    return client_sock


def serve_client(client_sock, request):
    pr = parse_request(request)
    if pr is None:
        write_response(client_sock, 'error', 'Неверный запрос')
    else:
        err_list = search_errors_re(pr)

        # Дополнительное задание - Линейный и бинарный поиск
        log = parse_log(pr)

        search_errors(log, pr)
        search_errors_binary(log, pr)
        # ---------------------------------------------------

        if err_list:
            mes = f'Найдено {len(err_list)} совпадений:'
            write_response(client_sock, 'success', mes, err_list)
        else:
            write_response(client_sock, 'error', 'Ничего не найдено')


def write_response(client_sock, status, message, response=[]):
    client_sock.sendall(json.dumps({"status": status,
                                    "mes": message,
                                    "data": response}).encode('utf-8'))


def start_server(ip=TCP_IP, port=TCP_PORT):
    with create_sock(ip, port) as sock:
        while True:
            print('Ждем соединения...')
            conn = accept_client_conn(sock)
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                else:
                    print(f'Запрос: {data.decode("utf-8")}')
                    serve_client(conn, data)
            print('-' * 30)
            conn.close()


if __name__ == '__main__':
    start_server(TCP_IP, TCP_PORT)


# Результат:
# $ python server.py
#
# Ждем соединения...
# Адрес клиента: ('127.0.0.1', 53241)
# ------------------------------
# Запрос: 23:12:56-Kernel
# search_errors: 0.0069141387939453125 ms
# search_errors_binary: 0.0019073486328125 ms
# Запрос: 17:08-TicketSubjectClean
# search_errors: 0.11491775512695312 ms
# search_errors_binary: 0.031948089599609375 ms
# Запрос: 12-Kernel::System::PostMaster::NewTicket::Run
# search_errors: 0.017881393432617188 ms
# search_errors_binary: 0.012874603271484375 ms
# Запрос: 22-Kernel
# search_errors: 1.5039443969726562 ms
# search_errors_binary: 0.5109310150146484 ms
# Запрос: 00-Kernel
# search_errors: 1.7631053924560547 ms
# search_errors_binary: 0.4191398620605469 ms
# Запрос: error
# ------------------------------
