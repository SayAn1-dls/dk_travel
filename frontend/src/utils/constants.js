/**
 * Application-wide constants
 */

export const APP_NAME = 'DK Travel';

export const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';

export const ITEMS_PER_PAGE = 12;

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
};

export const AUTH_TOKEN_KEY = 'dk_travel_token';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DESTINATIONS: '/destinations',
  TRIPS: '/trips',
  PROFILE: '/profile',
};
