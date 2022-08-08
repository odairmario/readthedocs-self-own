import os
def env(key,default_value="",is_bool=False):
    """get env variable
    """


    if is_bool:
        value = os.getenv(key, str(default_value)).lower() in ('true', '1', 't')
    else:
        value =  os.environ.get(key,default_value);

    return value
