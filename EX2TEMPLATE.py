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


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def test(actual_result, expected_result, function_name):
    status = STATUS_SUCCESS
    try:
        if isinstance(actual_result, list):
            lines = expected_result.split()
            for line_num, expected_line in enumerate(lines):
                if expected_line != actual_result[line_num]:
                    status = STATUS_FAILURE
                    p(f"line #{line_num}: expecting {expected_line} found {actual_result[line_num]}")

        elif isinstance(expected_result, (int, float)) and isinstance(actual_result, (int, float)):
            status = abs(expected_result - actual_result) >= EPSILON

        elif isinstance(expected_result, str) and isinstance(actual_result, str):
            status = expected_result != actual_result

        else:
            status = STATUS_FAILURE
    except TypeError:
        status = STATUS_FAILURE

    status_text = "OK" if status == STATUS_SUCCESS else "Failure"
    msg = f"Testing {function_name} ,expected_result= {expected_result} ,actual_result={actual_result} " + \
          f",result= {status_text}"

    current_dir = os.getcwd()
    original_student_file = os.path.join(current_dir, "STUDENT_FILE.py")
    function_name, _ = function_name.split('(')
    recursive_status, recursive_comment = test_if_recursive(original_student_file, function_name)

    if recursive_status == STATUS_FAILURE:
        status = STATUS_FAILURE
        if len(msg):
            msg += ";"
        msg += f"{recursive_comment}"

    status_text = "OK" if status == STATUS_SUCCESS else "Failed"
    p(f"test(): status= {status_text} ,msg= {msg}")
    return status, msg


def test_if_recursive(file_name, function):
    # p(f"test_if_recursive(): {function}")
    rv = False
    msg = None
    state = "before function"
    with open(file_name) as file_handler:
        for line in file_handler:
            if f"{function}(" in line:
                if state == "in function":
                    state = "found_recursive_call"
                    # p(f"line= {line} ,state0= {state}")
                    break

                if "def " in line and f"{function}(" in line and state == "before function":
                    state = "in function"
                    # p(f"line= {line} ,state1= {state}")

                if state != "in function":
                    break
        if state != "found_recursive_call":
            rv = True
            msg = f"Found a problem: {function}() is not recursive!"

    return rv, msg


def p(msg, should_exit=False):
    if should_exit:
        msg += " .Quitting"
    print(f"{datetime.now().time()} {msg}", file=sys.stderr)
    if should_exit:
        sys.exit(-1)


def tests():
    tests_list = []
    grade_per_test = 10
    grade_number = 100
    grade_comment = ""

    # 1
    try:
        tests_list.append([multiple(3, 4), 3 * 4, "multiple(3 * 4)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find multiple()"
        grade_number -= grade_per_test

    # 2
    try:
        tests_list.append([power(3, 4), math.pow(3, 4), "power(3, 4)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find power()"
        grade_number -= grade_per_test
    # 3
    try:
        tests_list.append([divide(25, 5), 5, "divide(25, 5)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find divide()"
        grade_number -= grade_per_test

    # 4
    try:
        tests_list.append([modulo_10(63), 3, "modulo_10(63)", grade_per_test])
        tests_list.append([modulo_10(0), 0, "modulo_10(0)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find modulo_10()"
        grade_number -= grade_per_test

    # 5
    try:
        tests_list.append([modulo_n(65, 4), 1, "modulo_n(65, 4)", grade_per_test])
        tests_list.append([modulo_n(64, 4), 0, "modulo_n(64, 4)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find modulo_n()"
        grade_number -= grade_per_test

    # 6
    try:
        with Capturing() as output:
            stars_length(123)
        tests_list.append([output[0], "***", "stars_length(123)", grade_per_test])

        with Capturing() as output:
            stars_length(9)
        tests_list.append([output[0], "*", "stars_length(9)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find stars_length()"
        grade_number -= grade_per_test

    # 7
    try:
        with Capturing() as output:
            stars(5)
        tests_list.append([output[0], "*****", "stars(5)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find stars()"
        grade_number -= grade_per_test

    # 8
    try:
        with Capturing() as output:
            triangleUpSideDown(5)
        tests_list.append([output, "*****\n****\n***\n**\n*\n", "triangleUpSideDown(5)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find triangleUpSideDown()"
        grade_number -= grade_per_test

    # 9
    try:
        with Capturing() as output:
            triangle(4)
        tests_list.append([output, "*\n**\n***\n****\n", "triangle(4)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find triangle()"
        grade_number -= grade_per_test

    # 10
    try:
        with Capturing() as output:
            reverse_number(123)
        tests_list.append([output[0], 321, "reverse_number(123)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find reverse_number()"
        grade_number -= grade_per_test

    # 11 and last
    try:
        with Capturing() as output:
            repeat_number(123)
        tests_list.append([output[0], 123, "repeat_number(321)", grade_per_test])
    except NameError:
        if len(grade_comment):
            grade_comment += ' ;'
        grade_comment += "Could not find repeat_number()"
        grade_number -= grade_per_test

    ######
    # Do the tests
    for a_test in tests_list:
        status, msg = test(a_test[0], a_test[1], a_test[2])
        if status == STATUS_FAILURE:
            grade_number -= a_test[3]
            if len(grade_comment):
                grade_comment += " ;"
            grade_comment += msg

    print(f"grade_number= {grade_number} ,grade_comment= {grade_comment}")


tests()
