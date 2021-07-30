
from dynaconf import Dynaconf, Validator

def check_sort_order(keys):
    valid_attrs = ['status', 'title', 'id', 'body', 'list_id', 'createdDateTime', 'dueDateTime', 'lastModifiedDateTime', 'importance', 'isReminderOn']
    for key in keys:
        if len(key) > 0 and key[0] == '-':
            # Then we need to chop out that char for validation
            key = key[1:]
        if key not in valid_attrs:
            return False
    return True


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
    validators=[
        Validator('To_Do_Widget', must_exist=True),
        Validator('To_Do_Widget.update_interval', is_type_of=int),
        Validator('To_Do_Widget.incomplete_task_visibility', is_type_of=bool),
        Validator('To_Do_Widget.lists_to_use', is_type_of=list),
        Validator('To_Do_Widget.task_sort_order', is_type_of=list),
        Validator('Weather_Widget', must_exist=True),
        Validator('Weather_Widget.city_name', is_type_of=str),
        Validator('Weather_Widget.units', is_type_of=str),
        Validator('Weather_Widget.update_interval', is_type_of=int),
        Validator('To_Do_Widget.task_sort_order', condition=check_sort_order)
    ],
)