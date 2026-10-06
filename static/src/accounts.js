// Optional presentation only. Native POSTs retain CSRF and authoritative checks.
document.documentElement.dataset.accountsEnhanced = "true";
const alert = document.querySelector('[role="alert"]');
if (alert) alert.focus();

const calendar = document.querySelector('[name="calendar"]');
const birthDate = document.querySelector('[name="birth_date"]');
if (calendar && birthDate) {
  const labelCalendar = () => {
    birthDate.placeholder = calendar.value === "jalali" ? "۱۳۶۸-۱۰-۱۱" : "1990-01-01";
  };
  calendar.addEventListener("change", labelCalendar);
  labelCalendar();
}

const resend = document.querySelector("[data-resend]");
const countdown = document.querySelector("[data-countdown]");
if (resend && countdown) {
  let remaining = Math.max(0, Math.min(3600, Number(resend.dataset.remaining) || 0));
  const update = () => {
    countdown.textContent = `زمان پیشنهادی تا درخواست دوباره: ${remaining} ثانیه`;
    resend.disabled = remaining > 0;
  };
  update();
  const timer = setInterval(() => {
    remaining = Math.max(0, remaining - 1);
    update();
    if (remaining === 0) clearInterval(timer);
  }, 1000);
}
