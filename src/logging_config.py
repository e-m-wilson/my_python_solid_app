import logging

def setup_logging():
    # will only run once on app startup, other calls have no effect 
    # and can conflict with other loggers/modules 
    # so we may as well centralize this
    logging.basicConfig(
        # This does NOT mean 'only log INFO messages'
        # It means 'log INFO and anything more severe'
        # Default log levels:
        # DEBUG, INFO, WARNING, ERROR, CRITICAL
        # So in this case, DEBUG will be filtered out
        level=logging.INFO,
        # this is C-style string formatting, used before we had f or r strings
        # %(key) = pull value from logging dictionary
        # %()s <- 's' format as string. There is also: d=int, f=float, r=repr(), x=hex
        # uses lazy formatting for increased write performance,
        # so for historical and performance reasons its still used for logs
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",

        # we could set the following to store logs to a file
        # this isn't recommended in prod.
        # you could also route it to a handler. (not shown)
        # by default (how it's setup now with filename commented out) logs are routed to sys.stderr
        # stderr is the standard error output stream in Python
        # this default (or stdout) is preferred, because we don't want our container to manage files internally
        # instead, once we host as a cloud-native app via AWS, heroku, etc, 
        # those platforms automatically capture stderr/stdout and can store/aggregate them
        # filename='app.log'
    )
