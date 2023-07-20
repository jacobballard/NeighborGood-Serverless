import os

def get_variable(name: str, default_value: bool | None = None) -> bool:
    
    true_ = ('true', '1', 't')  # Add more entries if you want, like: `y`, `yes`, `on`, ...
    false_ = ('false', '0', 'f')  # Add more entries if you want, like: `n`, `no`, `off`, ...
    value: str | None = os.getenv(name, None)
    print(value)
    print('value')
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_