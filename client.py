import socket
import json

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024


def recvall(sock):
    """Вычитываем все данные из сокета"""

    bin_data = bytearray()

    while True:
        part = sock.recv(BUFFER_SIZE)
        bin_data += part
        if len(part) < BUFFER_SIZE:
            break

    return bin_data


def print_response(bin_data):
    """Вывод форматированного ответа сервера"""

    try:
        resp = json.loads(bin_data.decode('utf-8'))
    except ValueError:
        print('Невалидный ответ от сервера')
    else:
        print(resp['mes'])
        if resp['status'] == 'success':
            for line in resp['data']:
                print(line.strip())


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print('Подключение...')
        try:
            sock.connect((TCP_IP, TCP_PORT))
        except ConnectionRefusedError:
            print('Не могу подключиться')
            exit(1)

        print('Выполнено')
        print('Ctrl-C чтобы выйти')
        print('-' * 30)

        while True:
            try:
                in_str = input('> ')
            except KeyboardInterrupt as k:
                print('\nВыключение')
                break
            else:
                if in_str != '':
                    sock.send(in_str.encode('utf-8'))
                    data = recvall(sock)
                    print_response(data)
                else:
                    break


# Результат:
# $ python3 client.py
#
# Подключение...
# Выполнено
# Ctrl-C чтобы выйти
# ------------------------------
# > 23:54-DB::CheckSessionID
# Найдено 6 совпадений:
# [Sun Apr  2 23:54:15 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# [Sun Apr  2 23:54:18 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# [Sun Apr  2 23:54:24 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# [Sun Apr  2 23:54:46 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# [Sun Apr  2 23:54:49 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# [Sun Apr  2 23:54:54 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
# > 23:12:56-Kernel
# Ничего не найдено
# > 17:08-TicketSubjectClean
# Найдено 1 совпадений:
# [Mon Apr  3 17:08:05 2017][Error][Kernel::System::Ticket::TicketSubjectClean][1136] Need TicketNumber!
# > 12-Kernel::System::PostMaster::NewTicket::Run
# Найдено 2 совпадений:
# [Mon Apr  3 12:02:02 2017][Error][Kernel::System::PostMaster::NewTicket::Run][86]
# Priority 3 does not exist, falling back to 3 normal!
# [Sun Aug  6 12:06:02 2017][Error][Kernel::System::PostMaster::NewTicket::Run][86]
# Priority 3 does not exist, falling back to 3 normal!
# > error
# Неверный запрос
