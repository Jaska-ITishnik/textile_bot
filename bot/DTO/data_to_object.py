from db.ORM_SHABLON import DB


class User(DB):
    def __init__(self,
                 first_name=None,
                 last_name=None,
                 type=None,
                 telegram_id=None
                 ):
        self.first_name = first_name
        self.last_name = last_name
        self.type = type
        self.telegram_id = telegram_id


class Employee(DB):
    def __init__(self,
                 first_name=None,
                 last_name=None,
                 position=None,
                 telegram_id=None,
                 status=None
                 ):
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.telegram_id = telegram_id
        self.status = status


class Task(DB):
    def __init__(self,
                 employee_name=None,
                 task_code=None,
                 image=None,
                 description=None,
                 status=None
                 ):
        self.task_code = task_code
        self.employee_name = employee_name
        self.image = image
        self.description = description
        self.status = status
