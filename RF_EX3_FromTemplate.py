# Amir Shahal, Jan 2024

from RF_EX3 import *
from datetime import datetime
from inspect import signature
from io import StringIO
import math
import os
import sys

EPSILON = 1e-5
STATUS_SUCCESS = False
STATUS_FAILURE = True

os.environ["PYTHONDONTWRITEBYTECODE"] = "True"
student_file = "RF_EX3.py"


class Test:
    def __init__(self, function, params, expected_results,
                 capture_output, max_grade, a_word_to_look_for):
        self.function = function
        self.params = params
        self.expected_results = expected_results
        self.capture_output = capture_output
        self.max_grade = max_grade
        self.actual_grade = max_grade # for now...
        self.a_word_to_look_for = a_word_to_look_for
        self.grade_per_test = round(max_grade / len(expected_results))
        self.grade_comment = ""

    def __test_if_function_contains_a_word(self):
        state = "before function"
        current_dir = os.getcwd()
        file_name = os.path.join(current_dir, student_file)
        with open(file_name, encoding="utf8") as file_handler:
            for line in file_handler:
                if f"{self.a_word_to_look_for}" in line:
                    if state == "in function":
                        state = "found_the_word"
                        break

                if "def " in line and f"{self.function.__name__}" in line and state == "before function":
                    state = "in function"

            if state != "found_the_word":
                self.actual_grade = 0
                self.grade_comment = f"Found a problem: {self.function}() does not use/call {self.a_word_to_look_for}"

    def __do_specific_test(self, params, expected_result):
        if self.capture_output:
            with Capturing() as actual_result:
                self.function()
        else:
            actual_result = self.function()
        try:
            default_failed_msg = f"{self.function.__name__}() expected_result= {nice(expected_result)} " +\
                                 f",actual_result={nice(actual_result)}"
            if isinstance(actual_result, list):
                if len(actual_result) != len(expected_result):
                    self.actual_grade -= self.grade_per_test
                    self.grade_comment = f"{self.function.__name__}() Expecting {len(expected_result)} lines, found {len(actual_result)}. "
                    if len(actual_result) and len(expected_result):
                        self.grade_comment += f"{self.function.__name__}() First line: expected {expected_result[0]}, found {actual_result[0]}. " + \
                                              f"Last line: expected {expected_result[-1]}, found {actual_result[-1]}"
                else:
                    for line_num, expected_line in enumerate(expected_result):
                        if str(expected_line) != str(actual_result[line_num]):
                            self.actual_grade -= self.grade_per_test
                            self.grade_comment = f"{self.function.__name__}() line #{line_num}: expecting {expected_line} found {actual_result[line_num]}"

            elif isinstance(expected_result, (int, float)) and isinstance(actual_result, (int, float, str)):
                if abs(expected_result - float(actual_result)) >= EPSILON:
                    self.actual_grade -= self.grade_per_test
                    if len(self.grade_comment):
                        self.grade_comment += " ;"
                    self.grade_comment += default_failed_msg
            elif isinstance(expected_result, str) and isinstance(actual_result, str):
                if expected_result != actual_result:
                    self.actual_grade -= self.grade_per_test
                    if len(self.grade_comment):
                        self.grade_comment += " ;"
                    self.grade_comment += default_failed_msg
            else:
                self.actual_grade -= self.grade_per_test
                if len(self.grade_comment):
                    self.grade_comment += " ;"
                self.grade_comment += default_failed_msg
        except (TypeError, ValueError):
            self.actual_grade -= self.grade_per_test
            if len(self.grade_comment):
                self.grade_comment += " ;"
            self.grade_comment += default_failed_msg

    def do_the_test(self):
        # First do all general tests for the function, then run the fnction
        # for each input and compare the results to the expected output

        grade_before_general_tests = self.actual_grade
        # Find if the function exists
        if not callable(self.function):
            self.actual_grade = 0
            self.grade_comment = f"{self.function} is not callable"
        else:
            # Function exists, verify the signature is as expected (number of perams)
            sig = signature(self.function)
            if len(sig.parameters) != len(self.params[0]):
                self.actual_grade = 0
                self.grade_comment = f"{self.function.__name__}(): expects {len(sig.parameters)}" + \
                                     f" instead of {len(self.params[0])}"
            else:
                # Signature is as expected, in case there is a need to find specific word
                # within the function - look for it (for recursive and other tests)
                if self.a_word_to_look_for is not None:
                    self.__test_if_function_contains_a_word()

                # either test_if_function_contains_a_word worked or it was not required
                # do the input-output tests
                if grade_before_general_tests == self.actual_grade:
                    for params, expected_result in zip(self.params, self.expected_results):
                        self.__do_specific_test(params, expected_result)


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
                detailed_msg = f"Expecting {len(expected_result)} lines, found {len(actual_result)}. "
                if len(actual_result) and len(expected_result):
                    detailed_msg += f"First line: expected {expected_result[0]}, found {actual_result[0]}. " + \
                                    f"Last line: expected {expected_result[-1]}, found {actual_result[-1]}"
            else:
                for line_num, expected_line in enumerate(expected_result):
                    if str(expected_line) != str(actual_result[line_num]):
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
    original_student_file = os.path.join(current_dir, student_file)

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



def test_signature(fun, expected_num_of_args):
    signature_bad_grade = 0
    signature_comment = ""
    sig = signature(fun)
    if len(sig.parameters) != expected_num_of_args:
        signature_bad_grade = 100
        signature_comment = f"{fun.__name__}(): bad signature. The function expects {len(sig.parameters)} " + \
                            f"parameters instead of {expected_num_of_args}"
    return signature_bad_grade, signature_comment

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


def ex3_tests():
    grade_per_test = 20
    grade_number = 0 # Earn it!

    # 1
    expected_result_1_40 = []
    for i in range(1, 41):
        expected_result_1_40.append(i)

    test1 = Test(print_in_loop_1_to_40, [[]], [expected_result_1_40], True, grade_per_test, "for")
    test1.do_the_test()
    grade_comment = test1.grade_comment
    grade_number += test1.actual_grade

    test2 = Test(print_in_while_1_to_40, [[]], [expected_result_1_40], True, grade_per_test, "while")
    test2.do_the_test()
    if len(grade_comment):
        grade_comment += "; "
    grade_comment += test2.grade_comment
    grade_number += test2.actual_grade

    # 3
    boom_expected_output = []
    for i in range(0, 101):
        if i % 7 == 0 or "7" in str(i):
            boom_expected_output.append(i)

    test3 = Test(boom, [[]], [boom_expected_output], True, grade_per_test, None)
    test3.do_the_test()
    if len(grade_comment):
        grade_comment += "; "
    grade_comment += test3.grade_comment
    grade_number += test3.actual_grade

    # 4
    fib_expected_output = []
    a, b = 0, 1
    while a < 10000:
        fib_expected_output.append(a)
        a, b = b, a + b

    test4 = Test(fib, [[]], [fib_expected_output], True, grade_per_test, None)
    test4.do_the_test()
    if len(grade_comment):
        grade_comment += "; "
    grade_comment += test4.grade_comment
    grade_number += test4.actual_grade

    # 5
    dec_print_expected_output = []
    for i in range(0, 51):
        if i % 10 == 0:
            dec_print_expected_output.append(i // 10)
        else:
            dec_print_expected_output.append(i / 10)

    test5 = Test(fib, [[]], [fib_expected_output], True, grade_per_test, None)
    test5.do_the_test()
    if len(grade_comment):
        grade_comment += "; "
    grade_comment += test5.grade_comment
    grade_number += test5.actual_grade

    return grade_number, grade_comment


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


def load_ex6_tests():
    tests_list = []
    grade_per_test = 25
    grade_number = 100
    grade_comment = ""
    file_with_2_lines = "file_with_2_lines"
    file_with_4_lines = "file_with_4_lines"

    # 1
    test_function = True
    try:
        assert callable(read_from_file)
    except NameError as error:
        grade_number -= grade_per_test
        grade_comment = str(error)
        test_function = False

    if test_function:
        signature_bad_grade, signature_comment = test_signature(read_from_file, 1)
        if signature_bad_grade == 100:
            grade_number -= grade_per_test
            grade_comment = signature_comment
        else:
            try:
                actual_file_line_by_line = []
                with open(__file__, encoding="utf8") as file_handler:
                    for line in file_handler.readlines():
                        actual_file_line_by_line.append(line.rstrip())
                actual_file_line_by_line.append("")

                with Capturing() as output:
                    read_from_file(__file__)
                tests_list.append([output, actual_file_line_by_line,
                              "read_from_file(__file__)", grade_per_test])
            except (NameError, UnicodeDecodeError) as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                if isinstance(error, UnicodeDecodeError):
                    grade_comment += "read_from_file() failed. Open file for reading using the following command: " +\
                                     "open(file, encoding=\"utf8\")"
                else:
                    grade_comment += str(error)
                grade_number -= grade_per_test

    # 2
    test_function = True
    try:
        assert callable(write_to_file)
    except NameError as error:
        grade_number -= grade_per_test
        if len(grade_comment):
            grade_comment += " ;"
        grade_comment += str(error)
        test_function = False

    if test_function:
        signature_bad_grade, signature_comment = test_signature(write_to_file, 2)
        if signature_bad_grade == 100:
            grade_number -= grade_per_test
            grade_comment = signature_comment
        else:
            try:
                file_as_str = '\n'.join(actual_file_line_by_line)
                file_name = 'tmp_file_ex6.txt'
                write_to_file(file_name, file_as_str)
                with Capturing() as output:
                    read_from_file(file_name)
                tests_list.append([output, actual_file_line_by_line,
                                  f"read_from_file(write_to_file({file_name}, (long string)", grade_per_test])
            except (NameError, UnicodeDecodeError, TypeError) as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                grade_comment += str(error)
                grade_number -= grade_per_test

    # 3
    test_function = True
    try:
        assert callable(read_3_lines)
    except NameError as error:
        grade_number -= grade_per_test
        if len(grade_comment):
            grade_comment += " ;"
        grade_comment += str(error)
        test_function = False

    if test_function:
        signature_bad_grade, signature_comment = test_signature(read_3_lines, 1)
        if signature_bad_grade == 100:
            grade_number -= grade_per_test
            grade_comment = signature_comment
        else:
            try:
                file_with_2_lines_expected_file_content = []
                with open(file_with_2_lines, 'w') as file_handler:
                    for i in range(1, 3):
                        file_handler.write(f"{i}\n")
                        file_with_2_lines_expected_file_content.append(f"{i}")

                with Capturing() as output:
                    read_3_lines(file_with_2_lines)
                tests_list.append([output, file_with_2_lines_expected_file_content,
                                   "read_3_lines(file_with_2_lines)", int(grade_per_test / 2)])
            except (NameError, UnicodeDecodeError, TypeError) as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                grade_comment += str(error)
                grade_number -= grade_per_test

            try:
                file_with_4_lines_expected_file_content = []
                with open(file_with_4_lines, 'w') as file_handler:
                    for i in range(1, 5):
                        file_handler.write(f"{i}\n")
                        if i < 4:
                            file_with_4_lines_expected_file_content.append(f"{i}")

                with Capturing() as output:
                    read_3_lines(file_with_4_lines)
                tests_list.append([output, file_with_4_lines_expected_file_content,
                                   "read_3_lines(file_with_4_lines)", int(grade_per_test / 2)])
            except (NameError, UnicodeDecodeError, TypeError) as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                grade_comment += str(error)
                grade_number -= grade_per_test

    # 4
    test_function = True
    try:
        assert callable(copy_paste)
    except NameError as error:
        grade_number -= grade_per_test
        if len(grade_comment):
            grade_comment += " ;"
        grade_comment += str(error)
        test_function = False

    if test_function:
        signature_bad_grade, signature_comment = test_signature(copy_paste, 2)
        if signature_bad_grade == 100:
            grade_number -= grade_per_test
            grade_comment = signature_comment
        else:
            try:
                new_dir = "temp_ex6_dir"
                if os.path.exists(new_dir):
                    for f in os.listdir(new_dir):
                        os.remove(os.path.join(new_dir, f))
                else:
                    os.mkdir(new_dir)
                file_in_new_dir = os.path.join(new_dir, file_with_2_lines)
                copy_paste(file_with_2_lines, new_dir)
                with Capturing() as output:
                    read_from_file(file_in_new_dir)

                tests_list.append([output, file_with_2_lines_expected_file_content,
                                   f"copy_paste(ile_with_2_lines, {new_dir})\nread_from_file(file_in_new_dir){file_in_new_dir}",
                                   grade_per_test])
            except (NameError, UnicodeDecodeError, TypeError, FileNotFoundError) as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                grade_comment += str(error)
                grade_number -= grade_per_test
            except PermissionError as error:
                if len(grade_comment):
                    grade_comment += ' ;'
                grade_comment += str(error) + " (did you provide directory as second argument? " + \
                                 "or maybe you are trying to open a directory insted of writing to it?)"
                grade_number -= grade_per_test

    if os.path.exists(file_with_2_lines):
        os.remove(file_with_2_lines)

    if os.path.exists(file_with_4_lines):
        os.remove(file_with_4_lines)
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
        grade_number, grade_comment = ex3_tests()
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
    elif "EX6." in student_file:
        tests_list, grade_number, grade_comment = load_ex6_tests()
    else:
        p(f"Can NOT figure which test to run on {student_file}", True)

    if "EX3." not in student_file:
        do_the_tests(tests_list, grade_number, grade_comment)


if __name__ == "__main__":
    main()
