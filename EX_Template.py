# Amir Shahal, Feb 2024

from STUDENT_FILE import *
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
student_file = "STUDENT_FILE.py"


class Test:
    def __init__(self, function, params, expected_results,
                 capture_output, a_word_to_look_for, max_grade):
        self.function = function
        self.params = params
        self.expected_results = expected_results
        self.capture_output = capture_output
        self.max_grade = max_grade
        self.actual_grade = max_grade  # for now...
        self.a_word_to_look_for = a_word_to_look_for
        self.grade_per_test = max_grade / len(expected_results)
        self.grade_comment = ""
        self.__do_the_test()

    def __str__(self):
        grade_comment_str = "None" if self.grade_comment == "" else self.grade_comment
        rv = f"Test {self.function.__name__}({nice(self.params)}): " + \
             f"grade_number= {round(self.actual_grade, 2)}/{self.max_grade}" + \
             f" ,grade_comment= {grade_comment_str}"
        return rv

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
        default_failed_msg = f"{self.function.__name__}() failed"
        try:
            if self.capture_output:
                with Capturing() as actual_result:
                    self.function(*params)
                if len(actual_result) == 1:
                    actual_result = actual_result[0]
            else:
                actual_result = self.function(*params)
            default_failed_msg = f"{self.function.__name__}() expected_result= {nice(expected_result)} " +\
                                 f",actual_result={nice(actual_result)}"
            if isinstance(actual_result, list):
                if len(actual_result) != len(expected_result):
                    self.actual_grade -= self.grade_per_test
                    self.grade_comment = f"{self.function.__name__}() Expecting {len(expected_result)} lines, " + \
                                         f"found {len(actual_result)}. "
                    if len(actual_result) and len(expected_result):
                        self.grade_comment += f"{self.function.__name__}() " + \
                                              f"First line: expected {expected_result[0]}, " + \
                                              f"found {actual_result[0]}. " + \
                                              f"Last line: expected {expected_result[-1]}, found {actual_result[-1]}"
                else:
                    grade_discarded = False
                    for line_num, expected_line in enumerate(expected_result):
                        if str(expected_line) != str(actual_result[line_num]):
                            if not grade_discarded:
                                # do once per test and not once per line
                                self.actual_grade -= self.grade_per_test
                                grade_discarded = True
                            self.grade_comment = f"{self.function.__name__}() line #{line_num}: " + \
                                                 f"expecting {expected_line} found {actual_result[line_num]}"

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
            elif actual_result is None:
                if expected_result is not None:
                    self.actual_grade -= self.grade_per_test
                    if len(self.grade_comment):
                        self.grade_comment += " ;"
                    self.grade_comment += default_failed_msg
            else:
                self.actual_grade -= self.grade_per_test
                if len(self.grade_comment):
                    self.grade_comment += " ;"
                self.grade_comment += default_failed_msg
        except (TypeError, ValueError, IndexError, NameError, PermissionError, FileNotFoundError, AttributeError) \
                as error:
            self.actual_grade -= self.grade_per_test
            if len(self.grade_comment):
                self.grade_comment += " ;"
            if type(error).__name__ == "PermissionError":
                error_str = f"{error}. Maybe you are writing to a directory?"
            else:
                error_str = str(error)
            self.grade_comment += f"{default_failed_msg} ,error= {error_str}"

    def __do_the_test(self):
        # First do all general tests for the function, then run the function
        # for each input and compare the results to the expected output

        grade_before_general_tests = self.actual_grade
        # Find if the function exists
        if not callable(self.function):
            self.actual_grade = 0
            self.grade_comment = f"{self.function} is not callable"
        else:
            # Function exists, verify the signature is as expected (number of params)
            sig = signature(self.function)
            if len(sig.parameters) != len(self.params[0]):
                self.actual_grade = 0
                self.grade_comment = f"{self.function.__name__}(): expects {len(sig.parameters)} params" + \
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


def p(msg, should_exit=False):
    if should_exit:
        msg += " .Quitting"
    print(f"{datetime.now().time()} {msg}", file=sys.stderr)
    if should_exit:
        sys.exit(-1)


def nice(str_in):
    # return a nice representation of the input
    str_out = str(str_in)
    if isinstance(str_in, list):
        str_out = ""
        for str_in_line in str_in:
            str_out += f"{str_in_line};"
        str_out = str_out[0:-1]

    if len(str_out) > 45:
        str_out = f"{str_out[0:40]} ...(truncated)"

    if str_out.strip() == "":
        str_out = f"({len(str_in)} white spaces)"
    return str_out


def the_test(tests_list, tests_grades_array=None):
    number_of_tests = len(tests_list)
    if number_of_tests == 0:
        msg = f"Could not find a valid test for {student_file}"
        p(f"Test failed. functionality_grade= 0 ,functionality_comment= {msg}")
        return 0, msg
    default_grade_per_test = round(100 / number_of_tests, 2)
    grade_number = 0  # Earn it!
    grade_comment = ""

    for test_num, test_params in enumerate(tests_list):
        test_grade = default_grade_per_test if tests_grades_array is None else tests_grades_array[test_num]
        a_test = Test(*test_params, test_grade)
        grade_number += a_test.actual_grade
        if len(grade_comment):
            grade_comment += "; "
        grade_comment += a_test.grade_comment
        p(a_test)

    grade_number = round(grade_number)
    grade_comment_str = "None" if grade_comment == "" else grade_comment
    p(f"functionality_grade= {grade_number} ,functionality_comment= {grade_comment_str}")
    return grade_number, grade_comment


def test_ex2():
    # Build outputs for specific tests
    triangle_up_side_down_expected_output = []
    for i in range(5, 0, -1):
        triangle_up_side_down_expected_output.append('*' * i)

    triangle_expected_output = []
    for i in range(1, 5):
        triangle_expected_output.append('*' * i)
    try:
        tests_list = [
            [multiple, [[3, 4], [1, 5]], [12, 5], False, 'multiple'],
            [power, [[3, 4], [1, 5]], [math.pow(3, 4), math.pow(1, 5)], False, 'power'],
            [divide, [[25, 5], [5, 1]], [5, 5], False, 'divide'],
            [modulo_10, [[63], [0]], [3, 0], False, 'modulo_10'],
            [modulo_n, [[65, 4], [64, 4]], [1, 0], False, 'modulo_n'],
            [stars_length, [[123], [9]], ['***', '*'], True, 'stars_length'],
            [stars, [[5]], ['*****'], True, 'stars'],
            [triangleUpSideDown, [[5]], [triangle_up_side_down_expected_output],
                True, 'triangleUpSideDown'],
            [triangle, [[4]], [triangle_expected_output],
             True, 'triangle'],
            [reverse_number, [[123]], [321], True, 'reverse_number'],
            [repeat_number, [[123]], [123], True, 'repeat_number'],
            ]

        the_test(tests_list)

    except NameError as error:
        p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
        # return 0, str(error)


def test_ex3():
    # Build expected outputs
    expected_result_1_40 = []
    for i in range(1, 41):
        expected_result_1_40.append(i)

    boom_expected_output = []
    for i in range(0, 101):
        if i % 7 == 0 or "7" in str(i):
            boom_expected_output.append(i)

    fib_expected_output = []
    a, b = 0, 1
    while a < 10000:
        fib_expected_output.append(a)
        a, b = b, a + b

    print_dec_expected_output = []
    for i in range(0, 51):
        if i % 10 == 0:
            print_dec_expected_output.append(i // 10)
        else:
            print_dec_expected_output.append(i / 10)

    try:
        tests_list = [
            [print_in_loop_1_to_40, [[]], [expected_result_1_40], True, "for"],
            [print_in_while_1_to_40, [[]], [expected_result_1_40], True, "while"],
            [boom, [[]], [boom_expected_output], True, None],
            [fib, [[]], [fib_expected_output], True, None],
            [print_dec, [[]], [print_dec_expected_output], True, None]
        ]
        the_test(tests_list)

    except NameError as error:
        p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
        # return 0, str(error)


def test_ex4():
    try:
        tests_list = [
            [donuts, [[4], [9], [10], [99]],
             ['Number of donuts: 4',
              'Number of donuts: 9',
              'Number of donuts: many',
              'Number of donuts: many'], False, None],

            [both_ends, [['spring'], ['Hello'], ['a'], ['xyz']],
             ['spng', 'Helo', '', 'xyyz'], False, None],

            [fix_start, [['babble'], ['aardvark'], ['google'], ['donut']],
             ['ba**le', 'a*rdv*rk', 'goo*le', 'donut'], False, None],

            [mix_up, [['mix', 'pod'], ['dog', 'dinner'], ['gnash', 'sport'], ['pezzy', 'firm']],
             ['pox mid', 'dig donner', 'spash gnort', 'fizzy perm'], False, None]


        ]
        the_test(tests_list)

    except NameError as error:
        p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
        return 0, str(error)


def test_ex5(tests_bitmap):
    tests_list = []
    if tests_bitmap & 1:
        try:

            # 1. match_ends
            # Given a list of strings, return the count of the number of
            # strings where the string length is 2 or more and the first
            # and last chars of the string are the same.

            tests_list.append([match_ends, [[['aba', 'xyz', 'aa', 'x', 'bbb']],
                              [['', 'x', 'xy', 'xyx', 'xx']],
                              [['aaa', 'be', 'abc', 'hello']]],
                              [3, 2, 1], False, None])

            # 2. front_x
            # Given a list of strings, return a list with the strings
            # in sorted order, except group all the strings that begin with 'x' first.
            # e.g. ['mix', 'xyz', 'apple', 'xanadu', 'aardvark'] yields
            # ['xanadu', 'xyz', 'aardvark', 'apple', 'mix']
            # Hint: this can be done by making 2 lists and sorting each of them
            # before combining them.

            tests_list.append(
                [front_x, [[['bbb', 'ccc', 'axx', 'xzz', 'xaa']],
                           [['xaa', 'xcc', 'aaa', 'bbb', 'ccc']],
                           [['mix', 'xyz', 'apple', 'xanadu', 'aardvark']]],
                          [['xaa', 'xzz', 'axx', 'bbb', 'ccc'],
                           ['xaa', 'xcc', 'aaa', 'bbb', 'ccc'],
                           ['xanadu', 'xyz', 'aardvark', 'apple', 'mix']],
                 False, None])

            # 3. sort_last
            # Given a list of non-empty tuples, return a list sorted in increasing
            # order by the last element in each tuple.
            # e.g. [(1, 7), (1, 3), (3, 4, 5), (2, 2)] yields
            # [(2, 2), (1, 3), (3, 4, 5), (1, 7)]
            # Hint: use a custom key= function to extract the last element form each tuple.

            tests_list.append([sort_last, [[[(1, 3), (3, 2), (2, 1)]],
                              [[(2, 3), (1, 2), (3, 1)]],
                              [[(1, 7), (1, 3), (3, 4, 5), (2, 2)]]],
                            [[(2, 1), (3, 2), (1, 3)],
                             [(3, 1), (1, 2), (2, 3)],
                             [(2, 2), (1, 3), (3, 4, 5), (1, 7)]], False, None])

        except NameError as error:
            p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
            # return 0, str(error)

    if tests_bitmap & 2:
        """

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

        """
        try:
            tests_list.append([remove_adjacent, [[[1, 2, 3]], [[2, 2, 3, 3, 3]], [[]]],
                               [[1, 2, 3], [2, 3], []], False, None])

            # 5. Given two lists sorted in increasing order, create and return a merged
            # list of all the elements in sorted order. You may modify the passed in lists.
            # Ideally, the solution should work in "linear" time, making a single
            # pass of both lists.
            #
            # NOTE - DO NOT use return sorted(sorted1 + sorted2) - that's too easy :-)
            #
            linear_merge1and2 = ['aa', 'bb', 'cc', 'xx', 'zz']
            linear_merge3 = ['aa', 'aa', 'aa', 'bb', 'bb']

            tests_list.append([linear_merge, [[['aa', 'xx', 'zz'], ['bb', 'cc']],
                                              [['aa', 'xx'], ['bb', 'cc', 'zz']],
                                              [['aa', 'aa'], ['aa', 'bb', 'bb']]
                                              ],
                              [linear_merge1and2, linear_merge1and2, linear_merge3], False, None])

        except NameError as error:
            p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
            # return 0, str(error)

    the_test(tests_list)


def test_ex6():
    this_file_as_list_of_lines = []
    with open(__file__, encoding="utf8") as file_handler:
        for line in file_handler.readlines():
            this_file_as_list_of_lines.append(line.rstrip())

    # Add empty line at the end
    this_file_as_list_of_lines.append("")

    # For write_to_file()
    file_as_str = '\n'.join(this_file_as_list_of_lines)
    file_name = 'tmp_file_ex6.txt'

    # for read_3_lines()
    file_with_4_lines_expected_file_content = []
    file_with_4_lines = "file_with_4_lines"
    with open(file_with_4_lines, 'w') as file_handler:
        for i in range(1, 5):
            file_handler.write(f"{i}\n")
            if i < 4:
                file_with_4_lines_expected_file_content.append(f"{i}")

    file_with_2_lines_expected_file_content = []
    file_with_2_lines = "file_with_2_lines"
    with open(file_with_2_lines, 'w') as file_handler:
        for i in range(1, 3):
            file_handler.write(f"{i}\n")
            file_with_2_lines_expected_file_content.append(f"{i}")

    # For copy_paste()
    new_dir = "tmp_ex6_dir"
    if os.path.exists(new_dir):
        for f in os.listdir(new_dir):
            os.remove(os.path.join(new_dir, f))
    else:
        os.mkdir(new_dir)

    file_in_new_dir = os.path.join(new_dir, file_with_2_lines)

    try:
        tests_list = [
            [read_from_file, [[__file__]], [this_file_as_list_of_lines], True, None],
            [write_to_file, [[file_name, file_as_str]], [None], False, None],

            # Now read what we wrote. Not perfect as if cuts write_to_file to two grades
            # each one of them with weight equal to a single test's weight but I guess
            # we can live with this.
            [read_from_file, [[file_name]], [this_file_as_list_of_lines], True, None],

            [read_3_lines, [[file_with_2_lines], [file_with_4_lines]],
             [file_with_2_lines_expected_file_content, file_with_4_lines_expected_file_content], True, None],

            [copy_paste, [[file_with_2_lines, new_dir]], [None], False, None],

            # same problem as above
            [read_from_file, [[file_in_new_dir]], [file_with_2_lines_expected_file_content], True, None],
        ]

        # the_test(tests_list, [25, 12.5, 12.5, 25, 12.5, 12.5])
        the_test(tests_list)

    except NameError as error:
        p(f"Test failed. functionality_grade= 0 ,functionality_comment= {error}")
        return 0, str(error)


def main():
    if "EX2." in student_file:
        test_ex2()
    elif "EX3." in student_file:
        test_ex3()
    elif "EX4." in student_file:
        test_ex4()
    elif "EX51." in student_file:
        test_ex5(1)
    elif "EX52." in student_file:
        test_ex5(2)
    elif "EX5" in student_file:
        test_ex5(3)
    elif "EX6." in student_file:
        test_ex6()
    else:
        p(f"Can NOT figure which test to run on {student_file}", True)


if __name__ == "__main__":
    # Test
    main()
