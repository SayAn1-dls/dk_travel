/**
 * Application-wide constants for DK Travel frontend.
 */

export const APP_NAME = 'DK Travel';
export const APP_TAGLINE = 'Your journey, your way.';

export const DESTINATIONS_PER_PAGE = 12;
export const POPULAR_DESTINATIONS_LIMIT = 6;

export const BOOKING_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  CANCELLED: 'cancelled',
  COMPLETED: 'completed',
};

export const SORT_OPTIONS = [
  { label: 'Rating (High to Low)', value: 'rating', order: -1 },
  { label: 'Price (Low to High)', value: 'price', order: 1 },
  { label: 'Price (High to Low)', value: 'price', order: -1 },
  { label: 'Name (A-Z)', value: 'name', order: 1 },
];

export const PAYMENT_METHODS = [
  { label: 'Credit Card', value: 'credit_card', icon: '💳' },
  { label: 'Debit Card', value: 'debit_card', icon: '💳' },
  { label: 'UPI', value: 'upi', icon: '📱' },
  { label: 'Net Banking', value: 'net_banking', icon: '🏦' },
  { label: 'Wallet', value: 'wallet', icon: '👛' },
];
