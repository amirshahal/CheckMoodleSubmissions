# Amir Shahal, Feb 2024

# 20240203, Todo:
# 1. Add timeout using Thread Timer.
# 2. Send Whatsapp message.
# 3. Take out student list to a csv. Done 20240208
# 4. Read from Moodle, write to Mashov.


import amirs_pycodestyle
import argparse
from datetime import datetime
import inspect
import glob
import os
# import openpyxl
import pandas as pd
import pickle
import re
import shutil
import subprocess
import sys
# import pywhatkit
import xlsxwriter

os.environ["PYTHONDONTWRITEBYTECODE"] = "True"


class Student:

    title = ["ציון מילולי", "ציון מספרי", "מספר מודל", "שם מקוצר", "מספר זהות", "שם בעברית", "מסד"]

    def __init__(self, meta_data_df):
        self.meta_data_df = meta_data_df
        self.grade_comment = None
        self.grade_number = None
        self.id = None
        self.moodle_id = None
        self.moodle_original_directory_name = None
        self.path = None
        self.short_name = None
        self.phone_number = None
        self.hebrew_name_from_moodle = None

    def set_ids_from_folder_name(self):
        self.hebrew_name_from_moodle = re.sub(r'[_a-zA-Z0-9]+', '', self.moodle_original_directory_name)
        p(f"now doing {self.hebrew_name_from_moodle}")
        try:
            self.id = str(self.meta_data_df[
                self.meta_data_df['HebrewMoodleName'] == self.hebrew_name_from_moodle]['ID'].values[0])

            self.short_name = self.meta_data_df[
                self.meta_data_df['HebrewMoodleName'] == self.hebrew_name_from_moodle]['ShortName'].values[0]

            self.phone_number = self.meta_data_df[
                self.meta_data_df['HebrewMoodleName'] == self.hebrew_name_from_moodle]['PhoneNumber'].values[0]

            if isinstance(self.phone_number, str) and self.phone_number == "":
                self.phone_number = None
            else:
                self.phone_number = str(int(self.phone_number))
                if self.phone_number.startswith('0'):
                    self.phone_number = self.phone_number[1:]
                self.phone_number = f"+972{self.phone_number}"
        except KeyError as error:
            p(f"self.set_ids_from_folder_name(): Failed to read ids from {args.students_personal_data_file} " +
              f"error message: {error}", True)

    def get_output_list(self):
        if isinstance(self.grade_comment, (list, tuple)):
            if len(self.grade_comment) == 1:
                if isinstance(self.grade_comment[0], (list, tuple)):
                    grade_comment = "; ".join(self.grade_comment[0])
                else:
                    grade_comment = self.grade_comment[0]
            else:
                grade_comment = "; ".join(self.grade_comment)
        else:
            grade_comment = self.grade_comment
        grade_comment = grade_comment.replace(': ;', ':')
        rv = [grade_comment, self.grade_number, self.moodle_id, self.short_name, self.id,
              self.hebrew_name_from_moodle]
        return rv

    def print_summary(self):
        sys.stderr.flush()
        msg = f"grade= {self.grade_number} ,comments= {self.grade_comment}"
        print(f"\t{msg}")
        print("--------------------")
        """
        if self.phone_number is not None and args.send_whatsapp:
            msg = f"Amir Shahal & Co. just checked your submission of {args.project_name} " + \
                  f"and here are the results:\n{msg}"
            pywhatkit.sendwhatmsg_instantly(self.phone_number, msg)
        """

    def __lt__(self, other):
        return self.short_name < other.short_name


class CheckStudentsSubmission:
    def __init__(self):
        self.students = []
        assert os.path.exists(args.students_personal_data_file), p(f"{args.students_personal_data_file} required " +
                                                                   "file does not exist", True)

        # keep_default_na is for Noam Aldema, AKA as NA which Pandas treat as NaN by default
        self.student_data_df = pd.read_excel(args.students_personal_data_file, keep_default_na=False)

        # Espeically for Noa Aldema :-). Pandas take NA as NaN. Go figure.
        # self.student_data_df.ShortName = self.student_data_df.ShortName.str.replace('"', '')

    def run(self):
        # Todo: unzip the latest downloaded zip file into "new_folder_name"

        self.load_students_data()

        self.test_students_code()

        self.write_excel_workbook()

    def write_excel_workbook(self):
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        workbook_name = os.path.join(args.path, f"{args.project}_{datetime_str}.xlsx")
        workbook = xlsxwriter.Workbook(workbook_name)

        # The workbook object is then used to add new
        # worksheet via the add_worksheet() method.
        worksheet = workbook.add_worksheet(datetime_str)

        for row, student in enumerate(self.students):
            col = 0
            if row == 0:
                for col, token in enumerate(student.title):
                    worksheet.write(0, col, token)
            for col, token in enumerate(student.get_output_list()):
                try:
                    worksheet.write(row + 1, col, token)
                except TypeError:
                    p("HERE")

            # #
            worksheet.write(row + 1, col + 1, row + 1)

        workbook.close()
        p(f"Wrote results for {len(self.students)} students to {workbook_name}")

    def check_file_name(self, file):
        if '_' not in file:
            print(f"\t\tExpecting file name with _, found {file}")
            return False

        if not file.endswith(".py"):
            print(f"\t\tExpecting file name ends with.py, found {file}")
            return False

        student_name, exercise_name = file[0:-3].split('_')

        if len(student_name) < 2 or len(student_name) > 3 or student_name.upper() != student_name:
            print(f"\t\tStudent name muse be 2 or 3 capital letters, found {student_name}")
            return False

        exercise_expected_name = self.get_expected_exercise_name()
        rv = True
        if exercise_name != exercise_expected_name:
            if exercise_expected_name == "EX5":
                if exercise_name != "EX51" and exercise_name != "EX52":
                    print(f"\t\tExpecting exercise name: EX51.py or EX52.py, found name: {exercise_name}")
                    rv = False
            else:
                print(f"\t\tExpecting exercise name: {exercise_expected_name}, found name: {exercise_name}")
                rv = False

        return rv

    @staticmethod
    def get_expected_exercise_name():
        assert "EX" in args.project, p(f"Expecting project contains EX, found {args.project}")
        index = args.project.find("EX") + 2
        rv = "EX"
        while args.project[index].isdigit():
            rv += args.project[index]
            index += 1
        return rv

    @staticmethod
    def build_file_from_template(full_file_name, exercise_code):
        file_basename = os.path.basename(full_file_name).replace(".py", "")
        student_dir_name = os.path.dirname(full_file_name)
        student_short_name, _ = file_basename.split("_")
        file_to_read = f"EX_TEMPLATE.py"
        file_to_write = os.path.join(student_dir_name, f"{student_short_name}_{exercise_code}_FromTemplate.py")
        with open(file_to_read, 'r') as reader_handler, open(file_to_write, 'w') as write_handler:
            for line in reader_handler.readlines():
                line = line.replace("STUDENT_FILE", file_basename)
                write_handler.write(line)
        p(f"Wrote {file_to_write}")
        return file_to_write

    @staticmethod
    def get_grades_from_text(text):
        last_word, grade, grade_comment = None, None, ""
        for word in text.split():
            if last_word is not None:
                if "functionality_grade=" in last_word:
                    grade = int(word)
                if ",functionality_comment=" in last_word:
                    grade_comment += f"{word} "
                    continue

            last_word = word

        # Take away the last space from grade_comment, if needed
        return grade, grade_comment.strip()

    def test_ex_using_template(self, full_file_name, exercise_code):
        temp_file = self.build_file_from_template(full_file_name, exercise_code)
        grade_to_discard = 0
        grade_text = ""
        result = None
        path = os.path.dirname(temp_file)
        current_wd = os.getcwd()
        os.chdir(path)
        try:
            result = subprocess.run(["python", temp_file],
                                    shell=True,
                                    capture_output=True,
                                    # timeout=10, # Does not work!
                                    text=True)
        except UnicodeDecodeError as error:
            grade_text = "An UnicodeDecodeError exception occurred:" + str(error)
            grade_to_discard = 100

        except Exception as error:
            grade_text = "An exception occurred:", type(error).__name__
            grade_to_discard = 100

        if not args.keep_templates:
            os.remove(temp_file)
        os.chdir(current_wd)
        if grade_to_discard == 0 and result is not None:
            if result.returncode == 0:
                grade, grade_text = self.get_grades_from_text(result.stderr)
                grade_to_discard = 100 - grade
            else:
                grade_text = f"Running {temp_file} returned {result.returncode} error: {result.stderr}"
                grade_to_discard = 100
        p(result.stderr)
        return grade_to_discard, grade_text
    """
    run full_file_name on input file and compare the results to output file.
    grade = 0 means perfect match
    grade = 100 means something doesn't work
    """
    def find_functionality_errors(self, full_file_name):
        grade_to_discard = 0
        grade_text = ""
        ex_name = None
        if "EX1." in full_file_name:
            ex_name = "EX1"
        elif "EX2." in full_file_name or \
             "EX3." in full_file_name or \
             "EX4." in full_file_name or \
             "EX5." in full_file_name or \
             "EX51." in full_file_name or \
             "EX52." in full_file_name or \
             "EX6." in full_file_name:
            exercise_name = None
            base_name = os.path.basename(full_file_name)
            match = re.search(r"EX(\d+)", base_name)

            if match:
                exercise_name = match.group(0)
            else:
                p(f"{full_file_name} is not a valid exercise name", True)
            grade_to_discard, grade_text = self.test_ex_using_template(full_file_name, exercise_name)
            return grade_to_discard, grade_text
        else:
            p(f"Do not know how to test {full_file_name}", True)

        input_file = f"<{ex_name}.input.txt"
        result = None
        try:
            result = subprocess.run(["python", full_file_name, input_file],
                                    shell=True,
                                    capture_output=True,
                                    text=True)
        except Exception as error:
            grade_text = "An exception occurred:", type(error).__name__
            grade_to_discard = 100
            print(grade_text)

        if grade_to_discard == 0 and result is not None:
            if result.returncode != 0:
                grade_text = f"Running {full_file_name}<{input_file} returned {result.returncode}"
                grade_to_discard = 100
            else:
                output_file = f"{ex_name}.output.txt"
                if args.rigid == "hard":
                    if result.stdout != open(output_file).read():
                        grade_text = f"Running {full_file_name}<{input_file} returned {result.stdout}"\
                                     f"which is different than the expected results at {output_file}"
                        grade_to_discard = 100
                else:
                    grade_to_discard, grade_text = self.find_functionality_errors_soft(result.stdout, output_file,
                                                                                       ex_name)
        return grade_to_discard, grade_text

    def find_functionality_errors_soft(self, results, output_file, ex_name):
        if ex_name == "EX1":
            return self.find_functionality_errors_soft_ex1(results, output_file)

        p(f"Do not know how to sot test {ex_name}", True)
        return None

    @staticmethod
    def get_name_and_age_from_text(text):
        # name is after Hello
        # age is before "years old
        # all case insensitive

        name, age, last_word, last_last_word = None, None, None, None
        regex_alphanumeric_only = re.compile('[^0-9a-zA-Z]')
        for word in text.split():
            word = regex_alphanumeric_only.sub('', word)
            if last_word is not None and "hello" in last_word.lower():
                name = word

            if last_last_word is not None and "old" in word.lower() and "years" in last_word.lower():
                age = float(last_last_word)

            last_last_word = last_word
            last_word = word
        return name, age

    def find_functionality_errors_soft_ex1(self, results, output_file):
        expected_output_text = open(output_file).read()
        name_result, age_result = self.get_name_and_age_from_text(results)
        name_expected, age_expected = self.get_name_and_age_from_text(expected_output_text)

        grade = 0
        grade_txt = ""
        if name_result is None or name_result != name_expected:
            grade += 50
            grade_txt = f"Expected {name_expected} ,found {name_result}\n"

        if age_result is None or age_result - age_expected > 1 or age_result - age_expected < 0:
            grade += 50
            if len(grade_txt):
                grade_txt += ", "
            grade_txt += f"Expected {age_expected} ,found {age_result}\n"

        return grade, grade_txt

    def test_files(self, valid_files):
        grade = 100
        errors = []

        for full_file_name in valid_files:
            print(f"\tTesting {full_file_name}")
            # Test functionality:
            fun_grade, fun_grade_text = self.find_functionality_errors(full_file_name)
            grade -= (fun_grade / len(valid_files))
            if fun_grade_text is not None and fun_grade_text != "None":
                errors.append(fun_grade_text)
                # p(fun_grade_text)

            pep8_checker = amirs_pycodestyle.Checker(full_file_name)
            list_of_pep8_errors = pep8_checker.check_all()
            if len(list_of_pep8_errors):
                if len(errors) == 1 and "None" in errors[0]:
                    errors.clear()
                errors.append(f"Found {len(list_of_pep8_errors)} pep8 errors: ")
                for error in list_of_pep8_errors:
                    errors.append(f"pep8 error in line {error[0]}, error type={error[2]} ,"
                                  f"error_message = {error[3]}")
                grade -= len(list_of_pep8_errors)

        grade = max(0, grade)
        if grade == 100:
            errors = "Perfect!"
        return grade, errors

    @staticmethod
    def get_max_files_expected():
        rv = None
        if "EX1." in args.project or \
           "EX2." in args.project or \
           "EX3." in args.project or \
           "EX4." in args.project or \
           "EX6." in args.project or \
           "EX7." in args.project:
            rv = 1
        elif "EX5." in args.project:
            rv = 2
        else:
            p(f"get_max_files_expected() Do not know how to handle project {args.project}", True)
        return rv

    def test_student_code(self, student):
        path = os.path.join(student.path, student.moodle_id)
        print(f"Testing {student.hebrew_name_from_moodle}:")
        files = os.listdir(path)
        max_files_expected = self.get_max_files_expected()
        if len(files) > max_files_expected:
            file_names = ",".join(files)
            student.grade_comment = f"Found {len(files)} files ({file_names}) while expecting only one file."
            student.grade_number = 0
        else:
            valid_files = []
            for file in sorted(os.listdir(path)):
                full_file_name = os.path.join(path, file)
                if self.check_file_name(file):
                    valid_files.append(full_file_name)
                else:
                    student.grade_comment = f"Found unexpected file name {file}"
                    student.grade_number = 0
                    break

            if len(valid_files):
                student.grade_number, student.grade_comment = self.test_files(valid_files)
            else:
                if student.grade_number is None:
                    # Currently this could not happen. In case a student's directory exists
                    # it contain at least one file (either with valid name or not).
                    # Still this case is for possible future Moodle change which may allow
                    # empty directory.
                    student.grade_comment = f"Could not find valid files to check."
                    student.grade_number = 0

        student.print_summary()

    def test_students_code(self):
        list_of_students_to_check = None
        if len(self.students) == 0:
            p(f"Something is totally wrong! No students found", True)
        for student in sorted(self.students):
            if args.student_short_name is None or args.student_short_name == student.short_name:
                if list_of_students_to_check is None:
                    list_of_students_to_check = self.student_data_df.ShortName.to_list()
                list_of_students_to_check.remove(student.short_name)
                self.test_student_code(student)

        # In case we test one student only, end here
        if args.student_short_name is not None:
            sys.exit(0)
        self.test_not_submitted(list_of_students_to_check)

    def test_not_submitted(self, list_of_students_to_check):
        # Now list_of_students_to_check contains the students that didn't submit :-(
        for student_hebrew_name in list_of_students_to_check.keys():
            student = Student(None)  # will it work?
            student.path = args.path
            student.hebrew_name_from_moodle = student_hebrew_name
            student.id = list_of_students_to_check[student_hebrew_name][0]
            student.short_name = list_of_students_to_check[student_hebrew_name][1]
            student.grade_number = 0
            student.grade_comment = "לא הוגש"
            self.students.append(student)

            print(f"Testing {student.hebrew_name_from_moodle}:")
            student.print_summary()

    @staticmethod
    def is_submission_folder(folder):
        return "_assignsubmission_file_" in folder

    @staticmethod
    def get_new_folder_name_from_current(folder_name):
        numbers = re.findall(r'\d{6}', folder_name)
        assert len(numbers) == 1, p(f"Could NOT find 6 consecutive digits in {folder_name}", True)
        return numbers[0]

    def load_students_data_from_original_sub_folders(self, df):
        for current_folder_name in os.listdir(args.path):
            if self.is_submission_folder(current_folder_name):
                student = Student(df)
                student.path = args.path
                student.moodle_original_directory_name = current_folder_name
                student.set_ids_from_folder_name()
                student.moodle_id = self.get_new_folder_name_from_current(current_folder_name)
                p(f"{self.__class__.__name__}::{inspect.getframeinfo(inspect.currentframe()).function}(): Changing "
                  f"{current_folder_name} to {student.moodle_id}")
                full_folder_current_name = os.path.join(args.path, current_folder_name)
                full_folder_new_name = os.path.join(args.path, student.moodle_id)
                os.rename(full_folder_current_name, full_folder_new_name)
                self.students.append(student)

        if len(self.students) == 0:
            p(f"No students submissions under {args.path}, maybe you forgot to extract data from the moodle?", True)

        with open(args.students_data_file, 'wb') as pickle_file_handler:
            pickle.dump(self.students, pickle_file_handler)

    def load_students_data(self):
        assert os.path.exists(args.path), p(f"{args.path} does not exist", True)

        if os.path.exists(args.students_data_file):
            with open(args.students_data_file, 'rb') as pickle_file_handler:
                self.students = pickle.load(pickle_file_handler)
        else:
            # get rid of the folder names and change them to mapping. Store the mapping in a pickle file
            self.load_students_data_from_original_sub_folders(self.student_data_df)


def main():
    check_students_submission = CheckStudentsSubmission()
    check_students_submission.run()


def clean_previous_outputs(path):
    for a_dir in os.listdir(path):
        full_path_dir = os.path.join(path, a_dir)
        if os.path.isdir(full_path_dir):
            pycache_dir = os.path.join(full_path_dir, "__pycache__")
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir)

            template_files = os.path.join(full_path_dir, "*FromTemplate*")
            for file in glob.glob(template_files):
                os.remove(file)

            for file in os.listdir(full_path_dir):
                if (("tmp" in file or "temp" in file) and "ex6" in file) or \
                        "file_with" in file:
                    full_file = os.path.join(full_path_dir, file)
                    if os.path.isfile(full_file):
                        os.remove(full_file)
                    if os.path.isdir(full_file):
                        shutil.rmtree(full_file)


def set_path(project):
    def get_creation_time(item_path):
        return os.path.getctime(item_path)

    exercise_name = None
    path = os.path.join(os.getenv('USERPROFILE'), 'Downloads', f"{project}")
    if not os.path.exists(path):
        path = None
        download_dir = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
        items = {os.path.join(download_dir, i) for i in os.listdir(download_dir) if i.startswith(project) and
                 os.path.isdir(os.path.join(download_dir, i))}
        sorted_items = sorted(items, key=get_creation_time)
        if len(sorted_items):
            path = sorted_items[-1]
            exercise_name = project.split('_')[-1]
            project = os.path.basename(path)

    return project, path, exercise_name


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep_templates", default=False, action='store_true')
    parser.add_argument("--send_whatsapp", default=False, action='store_true')
    parser.add_argument("--project", required=True)
    parser.add_argument("--rigid", default="hard")
    parser.add_argument("--student_short_name", default=None)
    parser.add_argument("--students_data_file", default="students_data.pkl")
    parser.add_argument("--students_personal_data_file", default="2023_2024.Bina2.xlsx")
    args_parsed = parser.parse_args()

    args_parsed.project, args_parsed.path, args_parsed.project_name = set_path(args_parsed.project)
    p(f"Checking {args_parsed.project_name} from {args_parsed.project}")
    args_parsed.students_data_file = os.path.join(args_parsed.path, args_parsed.students_data_file)
    assert args_parsed.rigid in (["hard", "soft"]), p(f"--rigid s/b hard or soft", True)

    clean_previous_outputs(args_parsed.path)

    return args_parsed


def p(msg, should_exit=False):
    if should_exit:
        msg += " .Quitting"
    print(f"{datetime.now().time()} {msg}", file=sys.stderr)
    if should_exit:
        sys.exit(-1)


if __name__ == "__main__":
    start_datetime = datetime.now()
    p(f"Started on {start_datetime}")
    args = read_args()
    main()
    end_datetime = datetime.now()
    exec_time = (end_datetime - start_datetime).total_seconds()
    p(f"Ended successfully on {end_datetime} after {round(exec_time, 2)} seconds")
