
from dynaconf import Dynaconf, Validator
from dynaconf.validator import ValidationError

from helpers.ArgHandler import Parse_Args, Get_Args

from logger.AppLogger import build_logger
logger = build_logger(logger_name="Dynaconf Settings", debug=Get_Args().verbose, use_logger_origin=False)

def check_sort_order(keys):
    """Validate that the sort order set in 'settings.toml' is exclusively made up of valid fields to sort on"""

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
)

def handle_dynaconf_validation_errors(validation_error):
    for error in validation_error.details:
        logger.error(f"The following settings error occurred: {error[1]}")
    logger.error("Program terminated due to configuration errors")
    exit(1)

# Set up validators to ensure that settings are set up properly and don't have errors
def create_dynaconf_validators():
    settings.validators.register(
        Validator('To_Do_Widget', must_exist=True),
        Validator('To_Do_Widget.update_interval', is_type_of=int),
        Validator('To_Do_Widget.incomplete_task_visibility', is_type_of=bool),
        Validator('To_Do_Widget.lists_to_use', is_type_of=list),
        Validator('To_Do_Widget.task_sort_order', is_type_of=list),
        Validator('To_Do_Widget.task_sort_order', condition=check_sort_order),
        Validator('To_Do_Widget.app_id', is_type_of=str, len_eq=36),
        Validator('Weather_Widget', must_exist=True),
        Validator('Weather_Widget.city_name', is_type_of=str),
        Validator('Weather_Widget.units', is_type_of=str),
        Validator('Weather_Widget.update_interval', is_type_of=int),
        Validator('Weather_Widget.api_key', must_exist=True, is_type_of=str, len_eq=32),
        Validator('Spotify_Widget', must_exist=True),
        Validator('Spotify_Widget.client_id', must_exist=True, is_type_of=str, len_eq=32),
        Validator('Spotify_Widget.client_secret', must_exist=True, is_type_of=str, len_eq=32)
    )

    try:
        settings.validators.validate_all()
    except ValidationError as e:
        handle_dynaconf_validation_errors(e)