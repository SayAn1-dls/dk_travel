# API Reference

Base URL: `https://dk-travel-api.onrender.com/api/v1`

## Authentication

| Method | Endpoint          | Description              |
|--------|-------------------|------------------------  |
| POST   | `/auth/register`  | Register a new user      |
| POST   | `/auth/login`     | Login and receive JWT    |
| POST   | `/auth/logout`    | Invalidate current token |
| GET    | `/auth/me`        | Get current user profile |

## Destinations

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| GET    | `/destinations`       | List all destinations          |
| GET    | `/destinations/:id`   | Get destination by ID          |
| POST   | `/destinations`       | Create a new destination       |
| PUT    | `/destinations/:id`   | Update destination             |
| DELETE | `/destinations/:id`   | Delete destination             |
| GET    | `/destinations/search`| Search destinations by query   |

## Trips

| Method | Endpoint           | Description                |
|--------|--------------------|--------------------------  |
| GET    | `/trips`           | List user trips            |
| GET    | `/trips/:id`       | Get trip details           |
| POST   | `/trips`           | Create a new trip          |
| PUT    | `/trips/:id`       | Update trip                |
| DELETE | `/trips/:id`       | Delete trip                |

## Users

| Method | Endpoint           | Description                |
|--------|--------------------|--------------------------  |
| GET    | `/users/profile`   | Get user profile           |
| PUT    | `/users/profile`   | Update user profile        |

## Notes
- All endpoints except `/auth/register` and `/auth/login` require a valid JWT in the `Authorization` header.
- Responses follow the format: `{ success: boolean, data: any, message: string }`
