import dis
import socket


class ClientMaker(type):
    def __new__(cls, name, bases, dct):
        # Проверьте все экземпляры при создании класса и выдайте ошибку, если они относятся к экземпляру сокета.
        for key, value in dct.items():
            if not hasattr(value, '__call__'):
                if isinstance(value, socket.socket):
                    raise ValueError(f'Сокет не может быть создан на уровне создания класса!')
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        sock_alias = ['sock', 'socket', 'client']
        com_fcn = ['get_message', 'send_message']
        forbidden_sock_cmd = ['accept', 'listen']
        class_methods = {}
        class_attrs = []
        found_com_fcn = False

        # Получить методы класса
        for key, value in dct.items():
            if hasattr(value, '__call__'):
                class_methods.update({key: value})

        # Получить атрибуты класса
        for instruction in dis.get_instructions(dct['__init__']):
            if instruction.opname == 'STORE_ATTR':
                class_attrs.append(getattr(instruction, 'argval'))

        # Проверьте, есть ли у клиента определение сокета в его инициализации.
        if not [class_attr for class_attr in class_attrs if class_attr in sock_alias]:
            raise ValueError(f'У клиента должен быть сокет!')

        # Проверьте каждый метод класса и проверьте, вызывался ли сокет с функциями приема или прослушивания.
        for class_method in class_methods.values():
            instructions = dis.get_instructions(class_method)
            sock_found = False
            for instruction in instructions:
                # Установите флаг, если используется какая-либо из функций связи
                if instruction.opname == 'LOAD_GLOBAL':
                    if instruction.argval in com_fcn:
                        found_com_fcn = True
                # Если вызов метода происходит сразу после загрузки сокета, а метод принимает
                # или слушает - выдает ошибку
                if sock_found:
                    if instruction.opname == 'LOAD_METHOD':
                        instruction_cmd = instruction.argval
                        if instruction_cmd in forbidden_sock_cmd:
                            raise TypeError(f'Использование метода {instruction_cmd} у сокета '
                                            f'недопустимо в классе {name}')
                    sock_found = False
                if instruction.opname == 'LOAD_ATTR' and instruction.argval in sock_alias:
                    sock_found = True
        # Проверьте, присутствует ли один из двух способов связи
        if not found_com_fcn:
            raise ValueError(f'Отсутствуют вызовы функций, работающих с сокетами')
        type.__init__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        for arg in args:
            if isinstance(arg, socket.socket):
                if arg.family != socket.AddressFamily.AF_INET or arg.type != socket.SocketKind.SOCK_STREAM:
                    raise ValueError(f'Сокеты должны использоваться для TCP')
        return super().__call__(*args, **kwargs)


class ServerMaker(type):
    def __init__(cls, name, bases, dct):
        sock_alias = ['sock', 'socket', 'server']
        com_fcn = ['get_message', 'send_message', 'process_message', 'process_client_message']
        forbidden_sock_cmd = ['connect', ]
        tcp_sock_cfg = ['AF_INET', 'SOCK_STREAM']
        class_methods = {}
        found_com_fcn = False

        # Получить методы класса
        for key, value in dct.items():
            if hasattr(value, '__call__'):
                class_methods.update({key: value})

        # Проверяет каждый метод класса и проверьте, вызывался ли сокет с функциями приема или прослушивания.
        for class_method in class_methods.values():
            instructions = dis.get_instructions(class_method)
            sock_found = False
            sock_arg_counter = 0
            for instruction in instructions:
                # Установика флаг, если используется какая-либо из функций связи
                if instruction.opname == 'LOAD_GLOBAL':
                    if instruction.argval in com_fcn:
                        found_com_fcn = True
                # Если вызов метода идет сразу после загрузки сокета и метод подключается - выдает ошибку
                if sock_found:
                    if instruction.opname == 'LOAD_METHOD':
                        instruction_cmd = instruction.argval
                        if instruction_cmd in forbidden_sock_cmd:
                            raise TypeError(f'Использование метода {instruction_cmd} у сокета '
                                            f'недопустимо в классе {name}')
                        if instruction_cmd == 'socket':
                            sock_arg_counter += 2  # Ожидание получения двух атрибутов от этой функции
                    sock_found = False
                # Если сокет был создан - проверьте 2 его аргумента, оба должны быть в конфигурации TCP
                if sock_arg_counter:
                    if instruction.opname == 'LOAD_ATTR':
                        sock_arg_counter -= 1
                        if instruction.argval not in tcp_sock_cfg:
                            raise TypeError(f'Использование {instruction.argval} у сокета недопустимо для работы по TCP'
                                            f' в классе {name}')
                    elif instruction.opname == 'CALL_METHOD':
                        sock_arg_counter = 0  # Метод был вызван до того, как были загружены ожидаемые аргументы
                if instruction.opname == 'LOAD_ATTR' and instruction.argval in sock_alias:
                    sock_found = True
        # Проверьте, присутствует ли один из двух способов связи
        if not found_com_fcn:
            raise ValueError(f'Отсутствуют вызовы функций, работающих с сокетами')
        type.__init__(cls, name, bases, dct)
