from enum import StrEnum

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    PHONE_ALREADY_EXISTS = "PHONE_ALREADY_EXISTS"
    INVALID_PHONE_FORMAT = "INVALID_PHONE_FORMAT"
    REQUIRED_FIELDS_MISSING = "REQUIRED_FIELDS_MISSING"
    INVALID_WORKSHOP = "INVALID_WORKSHOP"
    TECHNICIAN_SPECIALIZATION_REQUIRED = "TECHNICIAN_SPECIALIZATION_REQUIRED"
    INVALID_USER_ROLE = "INVALID_USER_ROLE"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ID_REQUIRED = "USER_ID_REQUIRED"
    INVALID_USER_ID_FORMAT = "INVALID_USER_ID_FORMAT"
    UNKNOWN_USER_ROLE = "UNKNOWN_USER_ROLE"
    TASK_DESCRIPTION_REQUIRED = "TASK_DESCRIPTION_REQUIRED"
    TECHNICIAN_REQUIRED = "TECHNICIAN_REQUIRED"
    TECHNICIAN_NOT_FOUND = "TECHNICIAN_NOT_FOUND"
    INVALID_TASK_DEADLINE = "INVALID_TASK_DEADLINE"
    PAST_TASK_DEADLINE = "PAST_TASK_DEADLINE"
    INVALID_TASK_PRIORITY = "INVALID_TASK_PRIORITY"
    TASK_CREATE_FORBIDDEN = "TASK_CREATE_FORBIDDEN"
    TASK_CROSS_WORKSHOP = "TASK_CROSS_WORKSHOP"
    TASK_LIST_FORBIDDEN = "TASK_LIST_FORBIDDEN"
    TASK_CROSS_WORKSHOP_ACCESS = "TASK_CROSS_WORKSHOP_ACCESS"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_EDIT_FORBIDDEN = "TASK_EDIT_FORBIDDEN"
    INVALID_TASK_EDIT_DATA = "INVALID_TASK_EDIT_DATA"
    TASK_EDIT_CROSS_WORKSHOP = "TASK_EDIT_CROSS_WORKSHOP"
    TASK_EDIT_BUSINESS_RULE = "TASK_EDIT_BUSINESS_RULE"
    TASK_LIST_ACCESS_ERROR = "TASK_LIST_ACCESS_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CURRENT_USER = "INVALID_CURRENT_USER"
    TASK_STATUS_FOREIGN = "TASK_STATUS_FOREIGN"
    TASK_STATUS_NOT_FOUND = "TASK_STATUS_NOT_FOUND"
    INVALID_TASK_STATUS = "INVALID_TASK_STATUS"
    TASK_STATUS_UNAUTHORIZED = "TASK_STATUS_UNAUTHORIZED"
    TASK_NOT_ASSIGNED_TO_USER = "TASK_NOT_ASSIGNED_TO_USER"
    PROFILE_EDIT_FOREIGN = "PROFILE_EDIT_FOREIGN"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    INVALID_PROFILE_DATA = "INVALID_PROFILE_DATA"
    INVALID_WORKSHOP_OR_SPECIALIZATION = "INVALID_WORKSHOP_OR_SPECIALIZATION"
    INVALID_FILTER_PARAMS = "INVALID_FILTER_PARAMS"
    FILTER_FORBIDDEN = "FILTER_FORBIDDEN"
    LOCAL_MESSAGE_MISSING = "LOCAL_MESSAGE_MISSING"
    LOCAL_MESSAGE_INCORRECT = "LOCAL_MESSAGE_INCORRECT"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.PHONE_ALREADY_EXISTS: "Пользователь с указанным номером телефона уже зарегистрирован",
    ErrorCode.INVALID_PHONE_FORMAT: "Неверный формат номера телефона",
    ErrorCode.REQUIRED_FIELDS_MISSING: "Заполните все обязательные поля",
    ErrorCode.INVALID_WORKSHOP: "Выбран некорректный цех",
    ErrorCode.TECHNICIAN_SPECIALIZATION_REQUIRED: "Для технического работника необходимо указать специализацию",
    ErrorCode.INVALID_USER_ROLE: "Выбрана недопустимая роль пользователя",
    ErrorCode.USER_NOT_FOUND: "Пользователь не найден",
    ErrorCode.USER_ID_REQUIRED: "Введите идентификатор пользователя",
    ErrorCode.INVALID_USER_ID_FORMAT: "Некорректный формат идентификатора",
    ErrorCode.UNKNOWN_USER_ROLE: "Невозможно определить права доступа пользователя",
    ErrorCode.TASK_DESCRIPTION_REQUIRED: "Необходимо указать описание задачи",
    ErrorCode.TECHNICIAN_REQUIRED: "Выберите исполнителя",
    ErrorCode.TECHNICIAN_NOT_FOUND: "Указанный исполнитель не найден",
    ErrorCode.INVALID_TASK_DEADLINE: "Некорректно указан срок выполнения",
    ErrorCode.PAST_TASK_DEADLINE: "Срок выполнения не может быть в прошлом",
    ErrorCode.INVALID_TASK_PRIORITY: "Выбран недопустимый приоритет задачи",
    ErrorCode.TASK_CREATE_FORBIDDEN: "Только начальник цеха может создавать задачи",
    ErrorCode.TASK_CROSS_WORKSHOP: "Нельзя назначить задачу сотруднику из другого цеха",
    ErrorCode.TASK_LIST_FORBIDDEN: "У вас нет прав на просмотр данного списка задач",
    ErrorCode.TASK_CROSS_WORKSHOP_ACCESS: "Доступ к задачам другого цеха запрещён",
    ErrorCode.TASK_NOT_FOUND: "Указанная задача не найдена",
    ErrorCode.TASK_EDIT_FORBIDDEN: "У вас нет прав на редактирование этой задачи",
    ErrorCode.INVALID_TASK_EDIT_DATA: "Введены некорректные данные задачи",
    ErrorCode.TASK_EDIT_CROSS_WORKSHOP: "Нельзя назначить задачу сотруднику из другого цеха",
    ErrorCode.TASK_EDIT_BUSINESS_RULE: "Изменение задачи невозможно из-за ограничений системы",
    ErrorCode.TASK_LIST_ACCESS_ERROR: "Обнаружена ошибка доступа к списку задач",
    ErrorCode.UNAUTHORIZED: "Для выполнения операции требуется авторизация",
    ErrorCode.INVALID_CURRENT_USER: "Некорректные данные текущего пользователя",
    ErrorCode.TASK_STATUS_FOREIGN: "Нельзя изменить статус задачи, назначенной другому сотруднику",
    ErrorCode.TASK_STATUS_NOT_FOUND: "Задача не найдена",
    ErrorCode.INVALID_TASK_STATUS: "Указан недопустимый статус задачи",
    ErrorCode.TASK_STATUS_UNAUTHORIZED: "Для изменения статуса необходимо войти в систему",
    ErrorCode.TASK_NOT_ASSIGNED_TO_USER: "Можно изменять только свои задачи",
    ErrorCode.PROFILE_EDIT_FOREIGN: "У вас нет прав на изменение чужого профиля",
    ErrorCode.PROFILE_NOT_FOUND: "Профиль сотрудника не найден",
    ErrorCode.INVALID_PROFILE_DATA: "Введены некорректные данные профиля",
    ErrorCode.INVALID_WORKSHOP_OR_SPECIALIZATION: "Некорректно указаны цех или специализация",
    ErrorCode.INVALID_FILTER_PARAMS: "Указаны некорректные параметры фильтрации",
    ErrorCode.FILTER_FORBIDDEN: "У вас нет прав на использование данного фильтра",
    ErrorCode.LOCAL_MESSAGE_MISSING: "Сообщение о результате операции не отображено",
    ErrorCode.LOCAL_MESSAGE_INCORRECT: "Отображено некорректное сообщение о результате операции",
}


ERROR_STATUS: dict[ErrorCode, int] = {
    ErrorCode.PHONE_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    ErrorCode.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.TECHNICIAN_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.TASK_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.TASK_STATUS_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.PROFILE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INVALID_CURRENT_USER: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.UNKNOWN_USER_ROLE: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.TASK_STATUS_UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.TASK_CREATE_FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_LIST_FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_CROSS_WORKSHOP_ACCESS: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_EDIT_FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_LIST_ACCESS_ERROR: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_STATUS_FOREIGN: status.HTTP_403_FORBIDDEN,
    ErrorCode.TASK_NOT_ASSIGNED_TO_USER: status.HTTP_403_FORBIDDEN,
    ErrorCode.PROFILE_EDIT_FOREIGN: status.HTTP_403_FORBIDDEN,
    ErrorCode.FILTER_FORBIDDEN: status.HTTP_403_FORBIDDEN,
}


class AppError(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        status_code: int | None = None,
        message: str | None = None,
        error_class: int = 1,
    ) -> None:
        self.error_code = error_code
        self.status_code = status_code or ERROR_STATUS.get(
            error_code, status.HTTP_400_BAD_REQUEST
        )
        self.message = message or ERROR_MESSAGES[error_code]
        self.error_class = error_class
        super().__init__(self.message)


def error_payload(error: AppError) -> dict[str, int | str]:
    return {
        "error_class": error.error_class,
        "error_code": error.error_code.value,
        "message": error.message,
    }


def validation_error_code(exc: RequestValidationError) -> ErrorCode:
    errors = exc.errors()
    missing_fields = {
        str(part)
        for error in errors
        if error.get("type") == "missing"
        for part in error.get("loc", ())
    }
    all_fields = {str(part) for error in errors for part in error.get("loc", ())}
    error_types = {str(error.get("type", "")) for error in errors}

    if "role" in all_fields:
        return ErrorCode.INVALID_USER_ROLE
    if "phone_number" in all_fields:
        return ErrorCode.INVALID_PHONE_FORMAT
    if "technician_id" in all_fields:
        if "missing" in error_types:
            return ErrorCode.TECHNICIAN_REQUIRED
        return ErrorCode.INVALID_USER_ID_FORMAT
    if "foreman_id" in all_fields or "user_id" in all_fields:
        if "missing" in error_types:
            return ErrorCode.USER_ID_REQUIRED
        return ErrorCode.INVALID_USER_ID_FORMAT
    if "task_id" in all_fields:
        if "missing" in error_types:
            return ErrorCode.TASK_NOT_FOUND
        return ErrorCode.INVALID_USER_ID_FORMAT
    if "task_description" in missing_fields:
        return ErrorCode.TASK_DESCRIPTION_REQUIRED
    if "specialization" in missing_fields:
        return ErrorCode.TECHNICIAN_SPECIALIZATION_REQUIRED
    if "start_time" in all_fields or "end_time" in all_fields:
        return ErrorCode.INVALID_TASK_DEADLINE
    if "important" in all_fields:
        return ErrorCode.INVALID_TASK_PRIORITY
    if "status" in all_fields:
        return ErrorCode.INVALID_TASK_STATUS
    return ErrorCode.REQUIRED_FIELDS_MISSING


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_payload(exc)),
    )


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error_code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        app_error = AppError(ErrorCode.UNAUTHORIZED, status_code=exc.status_code)
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        app_error = AppError(ErrorCode.TASK_LIST_FORBIDDEN, status_code=exc.status_code)
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        app_error = AppError(ErrorCode.USER_NOT_FOUND, status_code=exc.status_code)
    else:
        app_error = AppError(
            ErrorCode.REQUIRED_FIELDS_MISSING,
            status_code=exc.status_code,
        )
    return JSONResponse(
        status_code=app_error.status_code,
        content=jsonable_encoder(error_payload(app_error)),
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    app_error = AppError(validation_error_code(exc))
    return JSONResponse(
        status_code=app_error.status_code,
        content=jsonable_encoder(error_payload(app_error)),
    )
