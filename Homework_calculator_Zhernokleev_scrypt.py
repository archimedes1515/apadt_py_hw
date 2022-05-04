from functools import reduce


class ExpressionError(Exception):  # кастомный exception
    pass


class CalcExpr:
    operation = {                       # задаем словарь допустимых операций
        '+': (1, lambda x, y: x + y),
        '-': (1, lambda x, y: x - y),
        '*': (2, lambda x, y: x * y),
        '/': (2, lambda x, y: x / y),
        '~': (3, lambda x: -x)
    }

    def __init__(self, str_expr):  # конструктор
        if str_expr == '':  # проверим, что передана не пустая строка
            raise ExpressionError('Введена пустая строка')
        else:
            buf_lst = list(str_expr)    # очистим от пробелов и добавим атрибуты
            while ' ' in buf_lst:
                buf_lst.remove(' ')
            self.str_expr = reduce(lambda a, x: a + x, buf_lst, '')
            self.stack = []
            self.out = []

    @staticmethod
    def tokenize(str_to_token):  # метод, разбивающий исходное выражение на токены
        token_list = []          # для дальнейшей обработки в алгоритме сортировочной станции
        i = 0
        while i < len(str_to_token):    # цикл,позволяющий корректно токенизировать числа
            if str_to_token[i].isdigit():   # (вещественные и состоящие из более одной цифры)
                token_list.append(str_to_token[i])  # и знаки операций, и кинуть exception для некорректного символа
                for j in range(i + 1, len(str_to_token)):
                    if str_to_token[j].isdigit():
                        token_list[-1] += str_to_token[j]
                    elif str_to_token[j] == '.':
                        if '.' not in token_list[-1] and str_to_token[j + 1].isdigit():
                            token_list[-1] += str_to_token[j]
                        else:
                            raise ExpressionError('Неверно введена десятичная точка')
                    else:
                        i = j - 1
                        break
                if j == (len(str_to_token) - 1) and str_to_token[j].isdigit():
                    break
            elif str_to_token[i] in CalcExpr.operation or str_to_token[i] in ['(', ')']:
                token_list.append(str_to_token[i])
            else:
                raise ExpressionError('Введен неверный символ')
            i += 1
        return token_list

    @staticmethod
    def is_float(check_str):    # статический метод: проверка, является ли аргумент вещественным числом
        try:
            float(check_str)
            return True
        except ValueError:
            return False

    def sort_station(self):  # реализация алгоритма сортировочной станции с википедии
        self.out = []
        token_list = CalcExpr.tokenize(self.str_expr)   # используем метод tokenize, чтобы получить список токенов
        self.expr_token_list = token_list
        for token in token_list:    # проходимся по токенам и производим действия в соответствии с алгоритмом
            if token.isdigit():     # т.е. закидываем в стэк/выходной массив, в зависимости от того, чем является токен
                self.out.append(int(token))
            elif CalcExpr.is_float(token):
                self.out.append(float(token))
            elif token == '(':
                self.stack.append(token)
            elif token == ')':
                try:
                    while self.stack[-1] != '(':    # или, например, выталкиваем из стэка, если встретили ')'
                        self.out.append(self.stack.pop())
                    self.stack.pop()
                except IndexError:
                    raise ExpressionError('В выражении неверно поставлен разделитель, либо не согласованы скобки')
            elif token in CalcExpr.operation:  # встретили оператор, значит пока на вершине стека op2
                if len(self.stack) > 0:        # сравниваем приоритеты ор1, ор2
                    while self.stack[-1] in CalcExpr.operation and (
                            CalcExpr.operation[self.stack[-1]][0] >= CalcExpr.operation[token][0]):
                        self.out.append(self.stack.pop())
                        if len(self.stack) == 0:
                            break
                self.stack.append(token)
        if all(x in CalcExpr.operation for x in self.stack):    # токены кончились
            while len(self.stack) > 0:
                self.out.append(self.stack.pop())
        else:
            raise ExpressionError('В выражении не согласованы скобки')
        return self.out

    def rev_polish_calcul(self):    # обратная польская запись, алгоритм описан на вики
        for x in self.out:
            if x in CalcExpr.operation and x != '~':    # операторы, работающие с двумя операндами из стэка
                operand_right, operand_left = self.stack.pop(), self.stack.pop()
                try:
                    self.stack.append(CalcExpr.operation[x][1](operand_left, operand_right))
                except ZeroDivisionError:
                    raise ZeroDivisionError('Произошло деление на ноль') from None
            elif x == '~':  # оператор, работающий с одним операндами
                self.stack.append(CalcExpr.operation[x][1](self.stack.pop()))
            else:   # операнд
                self.stack.append(x)
        return self.stack


if __name__ == "__main__":
    print('''Это программа-калькулятор, считает значение математического выражения.
    Выражение должно содержать целые (123) и дробные числа (13.45), скобки, операции +, -, /, *.
    Также выражение может содержать унарный минус.
    Программа реализована с использованием обратной польской записи и алгоритма сортировочной станции.
    Обратная польская запись не позволяет использование одних и тех же знаков для записи унарных и
    бинарных операций (см. Вики), поэтому для ввода унарного минуса используйте знак "~"
    Примеры выражений: 15 + (16.3 -8)/2 +4*3- 5*3 /ответ должен быть равен 16.15/
            (~227+1.568)*(~32.2*(~12.28-(~1.337)))/((15.26 + 8)-19 ) /ответ: -18646.53908619719/''')
    print('-' * 90, '\n')
    print('Введите ваше выражение:')
    expression = input()

    calc_instance = CalcExpr(expression)
    print('Исходное выражение без пробелов:', calc_instance.str_expr, '\n')
    print('Результат работы алгоритма сортировочной станции:',
          *calc_instance.sort_station(), '\n')
    print('Значение введенного математического выражения:', calc_instance.rev_polish_calcul()[0])
