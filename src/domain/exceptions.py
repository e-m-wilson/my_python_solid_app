class AppErrorException(Exception):
    pass

class NotFoundException(AppErrorException):
    pass

class PermissionDeniedException(AppErrorException):
    pass
