export const normalizePhoneNumber = (phoneNumber: string) => {
  const cleaned = phoneNumber.replace(/[\s\-()]/g, "").trim();
  if (/^8\d{10}$/.test(cleaned)) {
    return `+7${cleaned.slice(1)}`;
  }
  if (/^7\d{10}$/.test(cleaned)) {
    return `+${cleaned}`;
  }
  return cleaned;
};
