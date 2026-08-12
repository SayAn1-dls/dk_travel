/**
 * Validate an email address.
 * @param {string} email
 * @returns {boolean}
 */
export const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Validate password meets minimum requirements.
 * @param {string} password
 * @returns {{ valid: boolean, errors: string[] }}
 */
export const validatePassword = (password) => {
  const errors = [];
  if (password.length < 8) errors.push('Must be at least 8 characters');
  if (!/[A-Z]/.test(password)) errors.push('Must contain an uppercase letter');
  if (!/[a-z]/.test(password)) errors.push('Must contain a lowercase letter');
  if (!/[0-9]/.test(password)) errors.push('Must contain a number');
  return { valid: errors.length === 0, errors };
};

/**
 * Validate phone number (Indian format).
 * @param {string} phone
 * @returns {boolean}
 */
export const isValidPhone = (phone) => {
  const regex = /^(\+91[\s-]?)?[6-9]\d{9}$/;
  return regex.test(phone.replace(/\s/g, ''));
};

/**
 * Validate date range for bookings.
 * @param {string|Date} checkIn
 * @param {string|Date} checkOut
 * @returns {{ valid: boolean, error: string }}
 */
export const validateDateRange = (checkIn, checkOut) => {
  const start = new Date(checkIn);
  const end = new Date(checkOut);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (start < today) return { valid: false, error: 'Check-in cannot be in the past' };
  if (end <= start) return { valid: false, error: 'Check-out must be after check-in' };
  return { valid: true, error: '' };
};
