Следует написать сервер и клиент с помощью socket

**Сервер:**

Сервер принимает от клиента строку в формате: ```HH[:MM[:SS]]-<some_string>```.

Данные те же, что в прошлом уроке: https://drive.google.com/file/d/0BxNmUtCDttnUT3ZJUFZWMHpuazA/edit

Сервер ищет по вхождению подстроки <some_string> в модуль

(тот, что ```Kernel::System::AuthSession::DB::CheckSessionID```)

и фильтрует по указанному времени. Ответ возвращается в виде JSON-массива, где элементы —

строки лога.

Например:

* ```12-Kernel::System::AuthSession::DB::CheckSessionID``` должен показать все записи,

где есть Kernel::System::AuthSession::DB::CheckSessionID в модуле с 12:00:00 по 12:59:59 за все даты

* ```17:08-TicketSubjectClean``` должен показать все записи, где в модуле присутствует подстрока

TicketSubjectClean с 17:08:00 по 17:08:59 за все даты

* ```23:12:56-Kernel``` должен показать все записи за секунду 23:12:56 за все даты, где модуль содержит Kernel

**Клиент:**

Принимает на вход строку формата ```HH[:MM[:SS]]-<some_string>```,

отправляет запрос на сервер, показывает ответ в виде:

Запрос:

```23:54-DB::CheckSessionID```

Ответ:

```
Найдено 6 совпадений:
[Sun Apr 2 23:54:15 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
[Sun Apr 2 23:54:18 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
[Sun Apr 2 23:54:24 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
[Sun Apr 2 23:54:46 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
[Sun Apr 2 23:54:49 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
[Sun Apr 2 23:54:54 2017][Error][Kernel::System::AuthSession::DB::CheckSessionID][49] Got no SessionID!!
```

**Усложнение (опционально):**

Сделать поиск в логе по времени или по модулю за логарифмическое время или быстрее.

Затратами на ОЗУ пренебречь (в разумных пределах)

Подсказка: гуглить индексы, деревья поиска, дихотомию