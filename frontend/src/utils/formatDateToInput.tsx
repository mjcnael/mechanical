function formatDateToInput(date: Date) {
  const pad = (num: number) => String(num).padStart(2, "0");
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export default formatDateToInput;
