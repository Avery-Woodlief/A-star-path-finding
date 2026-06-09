class MenuErrors(Exception):
    def __init__(self):
        super().__init__()
        self.message = "Menu Error"

    def print_generic(self):
        return "Menu Error"

class BadDropDownItemTypeError(MenuErrors):
    def __init__(self):
        super().__init__()
        self.message = "Bad drop down item type"
    def __str__(self):
        traceback = self.__traceback__

        if traceback is None:
            return ""

        while traceback.tb_next:
            traceback = traceback.tb_next

        file_name = traceback.tb_frame.f_code.co_filename
        function_name = traceback.tb_frame.f_code.co_name
        line_number = traceback.tb_lineno
        return f"{super().print_generic().upper()}\nIn {file_name}\n\tIn {function_name} on line {line_number}\n\t{self.message}"

class NoParentContainerFound(MenuErrors):
    def __init__(self):
        super().__init__()
        self.message = "No parent container found"
    def __str__(self):
        traceback = self.__traceback__

        if traceback is None:
            return ""

        while traceback.tb_next:
            traceback = traceback.tb_next

        file_name = traceback.tb_frame.f_code.co_filename
        function_name = traceback.tb_frame.f_code.co_name
        line_number = traceback.tb_lineno
        return f"{super().print_generic().upper()}\nIn {file_name}\n\tIn {function_name} on line {line_number}\n\t{self.message}"

