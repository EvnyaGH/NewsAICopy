# NewsAI — Frontend

NewsAI frontend part

## Requirements

- Node.js (LTS) and npm installed

## Run (dev)

Open a terminal and run:

1. Change to the frontend folder:
   `cd frontend`
2. Install dependencies:
   `npm install`
3. Start the dev server:
   `npm run dev`

Open the URL printed by Vite (default `http://localhost:5173`).

## Build (production)

From `frontend`:

- Create a production build:
  `npm run build`
- Preview the build locally:
  `npm run preview`

## Notes

- Set the backend API URL in an environment variable : `VITE_API_BASE_URL` in a `.env` file
  inside `frontend`.
