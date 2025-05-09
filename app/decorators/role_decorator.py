def required_role(role):
    def decorator(function):
        def wrapper():

            re