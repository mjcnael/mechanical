export type CurrentUser = {
  role: "foreman" | "technician";
  user_id: number;
  full_name: string;
  phone_number?: string;
  workshop?: string | null;
};

const TOKEN_KEY = "access_token";
const USER_KEY = "current_user";

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const setCurrentUser = (user: CurrentUser) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getCurrentUser = (): CurrentUser | null => {
  const rawUser = localStorage.getItem(USER_KEY);
  if (!rawUser) return null;

  try {
    return JSON.parse(rawUser) as CurrentUser;
  } catch {
    return null;
  }
};

export const logout = () => {
  clearToken();
};
