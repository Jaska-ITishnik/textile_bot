from aiogram.fsm.state import StatesGroup, State


class TaskAddForm(StatesGroup):
    task_code = State()
    photo = State()
    description = State()


class TaskDeleteForm(StatesGroup):
    id = State()


class TaskUpdateForm(StatesGroup):
    description = State()
    task_code = State()
    photo = State()


class EmployeeDeleteForm(StatesGroup):
    pk = State()


class EmployeeAddForm(StatesGroup):
    telegram_id = State()
    first_name = State()
    last_name = State()
    position = State()


class EmployeeUpdateForm(StatesGroup):
    telegram_id = State()
    first_name = State()
    last_name = State()
    position = State()


class GetEmployeeIdForm(StatesGroup):
    employee_id = State()


class GetTelegramIDForm(StatesGroup):
    telegram_id = State()


class GetTaskIDForm(StatesGroup):
    task_id = State()


class GetUserInfoForm(StatesGroup):
    first_name = State()
    last_name = State()
    type = State()
    telegram_id = State()


class GetUserTelegramId(StatesGroup):
    telegram_id = State()


class GetEditTaskCode(StatesGroup):
    task_code = State()


class GetDeleteTaskCode(StatesGroup):
    task_code = State()


class GetListTaskCode(StatesGroup):
    task_code = State()
