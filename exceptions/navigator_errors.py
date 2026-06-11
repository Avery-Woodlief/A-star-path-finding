class BaseNavigatorError(Exception):
    def __init__(self):
        super().__init__()
        self.message = "Navigator Error"

    def __str__(self):
        return "Navigator Error"

    def get_info(self):
        traceback = self.__traceback__

        if traceback is None:
            return ""

        while traceback.tb_next:
            traceback = traceback.tb_next

        file_name = traceback.tb_frame.f_code.co_filename
        function_name = traceback.tb_frame.f_code.co_name
        line_number = traceback.tb_lineno
        return f"{self.parent_message.upper()}\nIn {file_name}\n\tIn {function_name} on line {line_number}\n\t{self.message}"

class EmptyPathError(BaseNavigatorError):

    def __init__(self):
        super().__init__()
        self.parent_message = self.message
        self.message = "Navigator path is completely empty"

    def __str__(self):
        return self.get_info()

class NextNodeError(BaseNavigatorError):
    
    def __init__(self):
        super().__init__()
        self.parent_message = self.message
        self.message = "Navigator cannot find a node to traverse to"

    def __str__(self):
        return self.get_info()
