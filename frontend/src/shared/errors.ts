export const ERROR_MESSAGES = {
  PHONE_ALREADY_EXISTS:
    "Пользователь с указанным номером телефона уже зарегистрирован",
  INVALID_PHONE_FORMAT: "Неверный формат номера телефона",
  REQUIRED_FIELDS_MISSING: "Заполните все обязательные поля",
  INVALID_WORKSHOP: "Выбран некорректный цех",
  TECHNICIAN_SPECIALIZATION_REQUIRED:
    "Для технического работника необходимо указать специализацию",
  INVALID_USER_ROLE: "Выбрана недопустимая роль пользователя",
  USER_NOT_FOUND: "Пользователь не найден",
  USER_ID_REQUIRED: "Введите идентификатор пользователя",
  INVALID_USER_ID_FORMAT: "Некорректный формат идентификатора",
  UNKNOWN_USER_ROLE: "Невозможно определить права доступа пользователя",
  TASK_DESCRIPTION_REQUIRED: "Необходимо указать описание задачи",
  TECHNICIAN_REQUIRED: "Выберите исполнителя",
  TECHNICIAN_NOT_FOUND: "Указанный исполнитель не найден",
  INVALID_TASK_DEADLINE: "Некорректно указан срок выполнения",
  PAST_TASK_DEADLINE: "Срок выполнения не может быть в прошлом",
  INVALID_TASK_PRIORITY: "Выбран недопустимый приоритет задачи",
  TASK_CREATE_FORBIDDEN: "Только начальник цеха может создавать задачи",
  TASK_CROSS_WORKSHOP: "Нельзя назначить задачу сотруднику из другого цеха",
  TASK_LIST_FORBIDDEN: "У вас нет прав на просмотр данного списка задач",
  TASK_CROSS_WORKSHOP_ACCESS: "Доступ к задачам другого цеха запрещён",
  TASK_NOT_FOUND: "Указанная задача не найдена",
  TASK_EDIT_FORBIDDEN: "У вас нет прав на редактирование этой задачи",
  INVALID_TASK_EDIT_DATA: "Введены некорректные данные задачи",
  TASK_EDIT_CROSS_WORKSHOP:
    "Нельзя назначить задачу сотруднику из другого цеха",
  TASK_EDIT_BUSINESS_RULE:
    "Изменение задачи невозможно из-за ограничений системы",
  TASK_LIST_ACCESS_ERROR: "Обнаружена ошибка доступа к списку задач",
  UNAUTHORIZED: "Для выполнения операции требуется авторизация",
  INVALID_CURRENT_USER: "Некорректные данные текущего пользователя",
  TASK_STATUS_FOREIGN:
    "Нельзя изменить статус задачи, назначенной другому сотруднику",
  TASK_STATUS_NOT_FOUND: "Задача не найдена",
  INVALID_TASK_STATUS: "Указан недопустимый статус задачи",
  TASK_STATUS_UNAUTHORIZED: "Для изменения статуса необходимо войти в систему",
  TASK_NOT_ASSIGNED_TO_USER: "Можно изменять только свои задачи",
  PROFILE_EDIT_FOREIGN: "У вас нет прав на изменение чужого профиля",
  PROFILE_NOT_FOUND: "Профиль сотрудника не найден",
  INVALID_PROFILE_DATA: "Введены некорректные данные профиля",
  INVALID_WORKSHOP_OR_SPECIALIZATION:
    "Некорректно указаны цех или специализация",
  INVALID_FILTER_PARAMS: "Указаны некорректные параметры фильтрации",
  FILTER_FORBIDDEN: "У вас нет прав на использование данного фильтра",
  LOCAL_MESSAGE_MISSING: "Сообщение о результате операции не отображено",
  LOCAL_MESSAGE_INCORRECT:
    "Отображено некорректное сообщение о результате операции",
} as const;

export type ErrorCode = keyof typeof ERROR_MESSAGES;

export const FALLBACK_ERROR_MESSAGE = "Заполните все обязательные поля";

type ApiErrorPayload = {
  error_code?: string;
  message?: string;
  detail?: unknown;
};

const isErrorCode = (code: string): code is ErrorCode => code in ERROR_MESSAGES;

export const getLocalErrorMessage = (code: string | undefined) => {
  if (code && isErrorCode(code)) {
    return ERROR_MESSAGES[code];
  }
  return FALLBACK_ERROR_MESSAGE;
};

export const resolveApiErrorMessage = (payload: unknown): string => {
  if (!payload || typeof payload !== "object") {
    return FALLBACK_ERROR_MESSAGE;
  }

  const data = payload as ApiErrorPayload;

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  if (typeof data.error_code === "string") {
    return getLocalErrorMessage(data.error_code);
  }

  if (data.detail && typeof data.detail === "object") {
    return resolveApiErrorMessage(data.detail);
  }

  return FALLBACK_ERROR_MESSAGE;
};
