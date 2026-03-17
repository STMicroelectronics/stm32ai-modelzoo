# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

class InvalidCrendetialsException(Exception):
    "Raised when a login fails due to credentials error"
    def __init__(self) -> None:
        super().__init__('Invalid credentials. Please verify.')

class BlockedAccountException(Exception):
    "Raised when a login fails multiple times and myST account is blocked due to credentials error"
    def __init__(self) -> None:
        super().__init__('myST detected multiple erroneous trials. Please change your password on st.com')

class LoginFailureException(Exception):
    def __init__(self, username: str, password: str, details:str='') -> None:
        username = '' if username is None else username
        password = '' if password is None else password

        msg = f"Fail to login with username: '{username}' and password: '{'*'*len(password)}'. {details}"
        super().__init__(msg)

### Server errors
class ServerError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class AnalyzeServerError(ServerError):
    def __init__(self, message) -> None:
        super().__init__(f"AnalyzeServerError: {message}")

class GenerateServerError(ServerError):
    def __init__(self, message) -> None:
        super().__init__(f"GenerateServerError: {message}")

class ValidateServerError(ServerError):
    def __init__(self, message) -> None:
        super().__init__(f"ValidateServerError: {message}")


# Generic type for Benchmark errors
class BenchmarkError(Exception):
    def __init__(self, message) -> None:
        super().__init__(f"BenchmarkError: {message}")
# Error linked to server side errors
class BenchmarkServerError(ServerError, BenchmarkError):
    def __init__(self, message) -> None:
        super().__init__(f"BenchmarkServerError: {message}")

class BenchmarkFailure(BenchmarkError):
    def __init__(self, board, message) -> None:
        super().__init__(f"Benchmark failed on board {board}: {message}")


class GenerateNbgFailure(ServerError):
    "Raised when  fails"
    def __init__(self, message) -> None:
        super().__init__(f'Optimization failed: {message}')
class ServerRouteNotFound(ServerError):
    def __init__(self, message) -> None:
        super().__init__(f"RouteNotRoundError: {message}")


### Functional errors
class ModelNotFoundError(Exception):
    def __init__(self, message) -> None:
        super().__init__(f"ModelNotFoundError: {message}")

class WrongTypeError(Exception):
    def __init__(self, value, expected_type) -> None:
        super().__init__(f"{type(value)} value received, expected: {expected_type}")

class InternalErrorThatShouldNotHappened(Exception):
    def __init__(self, why) -> None:
        super().__init__(why)

# Error linked to wrong parameter type/values 
class ParameterError(Exception):
    def __init__(self, why) -> None:
        super().__init__(why)


class BenchmarkParameterError(ParameterError, BenchmarkError):
    def __init__(self, board, message) -> None:
        super().__init__(f"Benchmark failed on board {board}: {message}")

class FileFormatError(Exception):
    def __init__(self, why) -> None:
        super().__init__(why)
