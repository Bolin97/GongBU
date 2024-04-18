export default function toFormatted(raw: string) {
  const zone = new Date().getTimezoneOffset() / 60;
  const local_time = new Date(raw).valueOf() - zone * 60 * 60 * 1000;
  const date = new Date(local_time);

  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const hour = date.getHours().toString().padStart(2, "0");
  const minute = date.getMinutes().toString().padStart(2, "0");
  const second = date.getSeconds().toString().padStart(2, "0");

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}
