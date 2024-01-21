# Amir Shahal, Jan 2024

from STUDENT_FILE import *
from datetime import datetime
from io import StringIO
import math
import os
import sys

EPSILON = 1e-5
STATUS_SUCCESS = False
STATUS_FAILURE = True

os.environ["PYTHONDONTWRITEBYTECODE"] = "True"
student_file = "STUDENT_FILE.py"


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def finally_a_test(a_test):
    actual_result = a_test[0]
    expected_result = a_test[1]
    function_name = a_test[2]
    should_test_if_recursive = a_test[4] if len(a_test) > 4 else False
    a_word_to_look_for = a_test[5] if len(a_test) > 5 else None
    p(f"Testing {function_name}")
    status = STATUS_SUCCESS
    detailed_msg = f" expected_result= {nice(expected_result)} ,actual_result={nice(actual_result)}"

    try:
        if isinstance(actual_result, list):
            if len(actual_result) != len(expected_result):
                status = STATUS_FAILURE
                detailed_msg = f"Expecting {len(expected_result)} lines, found {len(actual_result)}. " + \
                               f"First line: expected {expected_result[0]}, found {actual_result[0]}. " + \
                               f"Last line: expected {expected_result[-1]}, found {actual_result[-1]}"
            else:
                for line_num, expected_line in enumerate(expected_result):
                    if expected_line != actual_result[line_num]:
                        status = STATUS_FAILURE
                        detailed_msg = f"line #{line_num}: expecting {expected_line} found {actual_result[line_num]}"

        elif isinstance(expected_result, (int, float)) and isinstance(actual_result, (int, float, str)):
            status = abs(expected_result - float(actual_result)) >= EPSILON

        elif isinstance(expected_result, str) and isinstance(actual_result, str):
            status = expected_result != actual_result

        else:
            status = STATUS_FAILURE
    except (TypeError, ValueError):
        status = STATUS_FAILURE

    status_text = "OK" if status == STATUS_SUCCESS else "Failure"
    msg = f"Testing {function_name} ,result= {status_text} ,details={detailed_msg}"

    #################
    # Additional tests, if needed
    current_dir = os.getcwd()
    original_student_file = os.path.join(current_dir, "STUDENT_FILE.py")

    if should_test_if_recursive:
        if "(" in function_name:
            function_name, _ = function_name.split('(')
        recursive_status, recursive_comment = test_if_recursive(original_student_file, function_name)

        if recursive_status == STATUS_FAILURE:
            status = STATUS_FAILURE
            if len(msg):
                msg += ";"
            msg += f"{recursive_comment}"

    if a_word_to_look_for is not None:
        word_test_status, word_test_comment = test_if_function_contains_a_word(original_student_file, function_name,
                                                                               a_word_to_look_for)

        if word_test_status == STATUS_FAILURE:
            status = STATUS_FAILURE
            if len(msg):
                msg += ";"
            msg += f"{word_test_comment}"

    status_text = "OK" if status == STATUS_SUCCESS else "Failed"
    p(f"test(): status= {status_text} ,msg= {msg}")
    return status, msg


def test_if_recursive(file_name, function):
    return test_if_function_contains_a_word(file_name, function, f"{function}(")


def test_if_function_contains_a_word(file_name, function, word):
    rv = False
    msg = None
    state = "before function"
    with open(file_name, encoding="utf8") as file_handler:
        for line in file_handler:
            if f"{word}" in line:
                if state == "in function":
                    state = "found_the_word"
                    break

            if "def " in line and f"{function}" in line and state == "before function":
                state = "in function"

        if state != "found_the_word":
            rv = True
            msg = f"Found a problem: {function}() does not use/call {word}"

    return rv, msg


def p(msg, should_exit=False):
    if should_exit:
        msg += " .Quitting"
    print(f"{datetime.now().time()} {msg}", file=sys.stderr)
    if should_exit:
        sys.exit(-1)


def nice(str_in):
    # return a nice representation of the input
    str_out = str_in
    if isinstance(str_in, list):
        str_out = ""
        for str_in_line in str_in:
            str_out += f"{str_in_line};"
        str_out = str_out[0:-1]

        if len(str_out) > 45:
            str_out = f"{str_out[0:40]} ...(truncated)"
    return str_out


def load_ex2_tests():
    tests_list = []
    grade_per_test = 10
    grade_number = 100
    grade_comment = ""

    # 1
    try:
        tests_list.append([multiple(3, 4), 3 * 4, "multiple(3 * 4)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 2
    try:
        tests_list.append([power(3, 4), math.pow(3, 4), "power(3, 4)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test
    # 3
    try:
        tests_list.append([divide(25, 5), 5, "divide(25, 5)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 4
    try:
        tests_list.append([modulo_10(63), 3, "modulo_10(63)", grade_per_test, True])
        tests_list.append([modulo_10(0), 0, "modulo_10(0)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 5
    try:
        tests_list.append([modulo_n(65, 4), 1, "modulo_n(65, 4)", grade_per_test, True])
        tests_list.append([modulo_n(64, 4), 0, "modulo_n(64, 4)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 6
    try:
        with Capturing() as output:
            stars_length(123)
        tests_list.append([output[0], "***", "stars_length(123)", grade_per_test, True])

        with Capturing() as output:
            stars_length(9)
        tests_list.append([output[0], "*", "stars_length(9)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 7
    try:
        with Capturing() as output:
            stars(5)
        tests_list.append([output[0], "*****", "stars(5)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 8
    triangle_up_side_down_expected_output = []
    for i in range(5, 0, -1):
        triangle_up_side_down_expected_output.append('*' * i)
    try:
        with Capturing() as output:
            triangleUpSideDown(5)
        tests_list.append(
            [output, triangle_up_side_down_expected_output, "triangleUpSideDown(5)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 9
    triangle_expected_output = []
    for i in range(1, 5):
        triangle_expected_output.append('*' * i)
    try:
        with Capturing() as output:
            triangle(4)
        tests_list.append([output, triangle_expected_output, "triangle(4)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 10
    try:
        with Capturing() as output:
            reverse_number(123)
        tests_list.append([output[0], 321, "reverse_number(123)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 11 and last
    try:
        with Capturing() as output:
            repeat_number(123)
        tests_list.append([output[0], 123, "repeat_number(123)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test
        grade_number = max(grade_number, 0)
    return tests_list, grade_number, grade_comment


def load_ex3_tests():
    tests_list = []
    grade_per_test = 20
    grade_number = 100
    grade_comment = ""

    # 1
    expected_result_1_40 = []
    for i in range(1, 41):
        expected_result_1_40.append(i)

    try:
        with Capturing() as output:
            print_in_loop_1_to_40()
            tests_list.append([output, expected_result_1_40, "print_in_loop_1_to_40", grade_per_test, False,
                               "for"])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 2
    try:
        with Capturing() as output:
            print_in_while_1_to_40()
            tests_list.append([output, expected_result_1_40, "print_in_while_1_to_40", grade_per_test, False,
                               "while"])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 3
    boom_expected_output = []
    for i in range(0, 101):
        if i % 7 == 0 or "7" in str(i):
            boom_expected_output.append(i)
    try:
        with Capturing() as output:
            boom()
        tests_list.append([output, boom_expected_output, "boom()", grade_per_test])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 4
    fib_expected_output = []
    a, b = 0, 1
    while a < 10000:
        fib_expected_output.append(a)
        a, b = b, a + b
    try:
        with Capturing() as output:
            fib()
        tests_list.append([output, fib_expected_output, "fib()", grade_per_test])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 5
    dec_print_expected_output = []
    for i in range(0, 51):
        if i % 10 == 0:
            dec_print_expected_output.append(i // 10)
        else:
            dec_print_expected_output.append(i / 10)

    try:
        with Capturing() as output:
            print_dec()
        tests_list.append([output, dec_print_expected_output, "print_dec()", grade_per_test])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    return tests_list, grade_number, grade_comment


def load_ex4_tests():
    tests_list = []
    grade_per_test = 6
    grade_number = 100
    grade_comment = ""

    # 1
    try:
        tests_list.append([donuts(4), 'Number of donuts: 4', "donuts(4)", grade_per_test, True])
        tests_list.append([donuts(9), 'Number of donuts: 9', "donuts(9)", grade_per_test, True])
        tests_list.append([donuts(10), 'Number of donuts: many', "donuts(10)", grade_per_test, True])
        tests_list.append([donuts(99), 'Number of donuts: many', "donuts(99)", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 2
    try:
        tests_list.append([both_ends('spring'), 'spng', "both_ends('spring')", grade_per_test, True])
        tests_list.append([both_ends('Hello'), 'Helo', "both_ends('Hello')", grade_per_test, True])
        tests_list.append([both_ends('a'), '', "both_ends('a')", grade_per_test, True])
        tests_list.append([both_ends('xyz'), 'xyyz', "both_ends('xyz')", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 3
    try:
        tests_list.append([fix_start('babble'), 'ba**le', "fix_start('babble')", grade_per_test, True])
        tests_list.append([fix_start('aardvark'), 'a*rdv*rk', "fix_start('aardvark')", grade_per_test, True])
        tests_list.append([fix_start('google'), 'goo*le', "fix_start('google')", grade_per_test, True])
        tests_list.append([fix_start('donut'), 'donut', "fix_start('donut')", grade_per_test, True])
    except NameError as error:

        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 4
    try:
        tests_list.append([mix_up('mix', 'pod'), 'pox mid', "mix_up('mix', 'pod')", grade_per_test, True])
        tests_list.append([mix_up('dog', 'dinner'), 'dig donner', "mix_up('dog', 'dinner')", grade_per_test, True])
        tests_list.append([mix_up('gnash', 'sport'), 'spash gnort', "mix_up('gnash', 'sport')", grade_per_test, True])
        tests_list.append([mix_up('pezzy', 'firm'), 'fizzy perm', "mix_up('pezzy', 'firm')", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    return tests_list, grade_number, grade_comment


def load_ex51_tests():
    tests_list = []
    grade_per_test = 11
    grade_number = 100
    grade_comment = ""

    # 1
    # A. match_ends
    # Given a list of strings, return the count of the number of
    # strings where the string length is 2 or more and the first
    # and last chars of the string are the same.

    try:
        # 1
        tests_list.append([match_ends(['aba', 'xyz', 'aa', 'x', 'bbb']), 3,
                           "match_ends(['aba', 'xyz', 'aa', 'x', 'bbb'])", grade_per_test])
        tests_list.append([match_ends(['', 'x', 'xy', 'xyx', 'xx']), 2,
                           "match_ends(['', 'x', 'xy', 'xyx', 'xx'])", grade_per_test])
        tests_list.append([match_ends(['aaa', 'be', 'abc', 'hello']), 1,
                           "match_ends(['aaa', 'be', 'abc', 'hello'])", grade_per_test])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 2
    # B. front_x
    # Given a list of strings, return a list with the strings
    # in sorted order, except group all the strings that begin with 'x' first.
    # e.g. ['mix', 'xyz', 'apple', 'xanadu', 'aardvark'] yields
    # ['xanadu', 'xyz', 'aardvark', 'apple', 'mix']
    # Hint: this can be done by making 2 lists and sorting each of them
    # before combining them.

    try:
        tests_list.append([front_x(['bbb', 'ccc', 'axx', 'xzz', 'xaa']),
                           ['xaa', 'xzz', 'axx', 'bbb', 'ccc'],
                            "front_x(['bbb', 'ccc', 'axx', 'xzz', 'xaa'])", grade_per_test])
        tests_list.append([front_x(['ccc', 'bbb', 'aaa', 'xcc', 'xaa']),
                           ['xaa', 'xcc', 'aaa', 'bbb', 'ccc'],
                          "front_x(['ccc', 'bbb', 'aaa', 'xcc', 'xaa'])", grade_per_test])
        tests_list.append([front_x(['mix', 'xyz', 'apple', 'xanadu', 'aardvark']),
                           ['xanadu', 'xyz', 'aardvark', 'apple', 'mix'],
                            "front_x(['mix', 'xyz', 'apple', 'xanadu', 'aardvark'])", grade_per_test])

    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test


    # 3
    # C. sort_last
    # Given a list of non-empty tuples, return a list sorted in increasing
    # order by the last element in each tuple.
    # e.g. [(1, 7), (1, 3), (3, 4, 5), (2, 2)] yields
    # [(2, 2), (1, 3), (3, 4, 5), (1, 7)]
    # Hint: use a custom key= function to extract the last element form each tuple.

    try:
        tests_list.append([sort_last([(1, 3), (3, 2), (2, 1)]),
                           [(2, 1), (3, 2), (1, 3)],
                            "sort_last([(1, 3), (3, 2), (2, 1)])", grade_per_test])
        tests_list.append([sort_last([(2, 3), (1, 2), (3, 1)]),
                           [(3, 1), (1, 2), (2, 3)],
                            "sort_last([(2, 3), (1, 2), (3, 1])", grade_per_test])
        tests_list.append([sort_last([(1, 7), (1, 3), (3, 4, 5), (2, 2)]),
                           [(2, 2), (1, 3), (3, 4, 5), (1, 7)],
                            "sort_last([(1, 7), (1, 3), (3, 4, 5), (2, 2)])", grade_per_test])

    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    return tests_list, grade_number, grade_comment


def load_ex52_tests():
    tests_list = []
    grade_per_test = 17
    grade_number = 100
    grade_comment = ""

    # 1
    try:
        # 1
        expected_remove_adjacent1 = []
        for i in range(1, 4):
            expected_remove_adjacent1.append(i)

        expected_remove_adjacent2 = []
        for i in range(2, 4):
            expected_remove_adjacent2.append(i)

        tests_list.append([remove_adjacent([1, 2, 2, 3]), expected_remove_adjacent1,
                           "remove_adjacent([1, 2, 2, 3])", grade_per_test, True])
        tests_list.append([remove_adjacent([2, 2, 3, 3, 3]), expected_remove_adjacent2,
                           "remove_adjacent([2, 2, 2, 3, 3])", grade_per_test, True])
        tests_list.append([remove_adjacent([]), [],
                           "remove_adjacent([])", grade_per_test, True])
    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    # 2
    linear_merge1 = ['aa', 'bb', 'cc', 'xx', 'zz']
    linear_merge2 = ['aa', 'bb', 'cc', 'xx', 'zz']
    linear_merge3 = ['aa', 'aa', 'aa', 'bb', 'bb']

    try:
        tests_list.append([linear_merge(['aa', 'xx', 'zz'], ['bb', 'cc']),
                           linear_merge1, "linear_merge(['aa', 'xx', 'zz'], ['bb', 'cc'])", grade_per_test, True])
        tests_list.append([linear_merge(['aa', 'xx'], ['bb', 'cc', 'zz']),
                           linear_merge2, "linear_merge(['aa', 'xx'], ['bb', 'cc', 'zz])", grade_per_test, True])
        tests_list.append([linear_merge(['aa', 'aa'], ['aa', 'bb', 'bb']),
                           linear_merge3, "linear_merge(['aa', 'aa'], ['aa', 'bb', 'bb'])", grade_per_test, True])

    except NameError as error:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += str(error)
        grade_number -= grade_per_test

    return tests_list, grade_number, grade_comment


def do_the_tests(tests_list, grade_number, grade_comment):
    for a_test in tests_list:
        status, msg = finally_a_test(a_test)
        if status == STATUS_FAILURE:
            grade_number -= a_test[3]
            if len(grade_comment):
                grade_comment += " ;"
            grade_comment += msg

    print(f"grade_number= {grade_number} ,grade_comment= {grade_comment}")


def main():
    tests_list, grade_number, grade_comment = None, None, None
    if "EX2." in student_file:
        tests_list, grade_number, grade_comment = load_ex2_tests()
    elif "EX3." in student_file:
        tests_list, grade_number, grade_comment = load_ex3_tests()
    elif "EX4." in student_file:
        tests_list, grade_number, grade_comment = load_ex4_tests()
    elif "EX5." in student_file:
        tests_list1, grade_number1, grade_comment1 = load_ex51_tests()
        tests_list2, grade_number2, grade_comment2 = load_ex52_tests()
        tests_list = tests_list1 + tests_list2
        grade_comment = f"{grade_comment1}"
        if len(grade_comment):
            grade_comment += ", "
        grade_comment += grade_comment2
        grade_number = round((grade_number1 + grade_number2) / 2)
    elif "EX51." in student_file:
        tests_list, grade_number, grade_comment = load_ex51_tests()
    elif "EX52." in student_file:
        tests_list, grade_number, grade_comment = load_ex52_tests()
    else:
        p(f"Can NOT figure which test to run on {student_file}", True)
    do_the_tests(tests_list, grade_number, grade_comment)


if __name__ == "__main__":
    main()
