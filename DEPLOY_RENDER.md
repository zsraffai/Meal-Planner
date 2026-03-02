# Deploy útmutató (Render - ingyenes)

Ez a projekt elő van készítve Render deployra a `render.yaml` fájllal.

## 1) Kód feltöltése GitHub-ra

A Render a GitHub repóból deployol.

## 2) Új Web Service létrehozása Renderen

1. Menj ide: https://render.com
2. New + → Blueprint
3. Válaszd ki a GitHub repót
4. Render beolvassa a `render.yaml`-t és felajánlja a szolgáltatást
5. Indítsd el a deployt

## 3) Kötelező environment változók

Render dashboardon állítsd be:

- `APP_PASSWORD` = a belépési jelszavad
- `DEEPSEEK_API_KEY` = DeepSeek API kulcs
- `GOOGLE_CLIENT_ID` = (opcionális, ha Google OAuth kell)
- `GOOGLE_CLIENT_SECRET` = (opcionális)
- `GOOGLE_REDIRECT_URI` = pl. `https://<app-nev>.onrender.com/auth/google/callback`

A `SECRET_KEY` automatikusan generálódik.

## 4) App elérése

Deploy után kapsz egy URL-t, pl:

- `https://meal-planner-v2.onrender.com`

## Fontos megjegyzés (SQLite)

Ez az app SQLite-ot használ (`meals.db`).
Render free környezetben a fájlrendszer nem tartós, ezért újraindulás/redeploy után az adatbázis elveszhet.

Ha tartós adatot szeretnél hosszú távon ingyen/kedvezőbben:
- válts külső DB-re (pl. Supabase Postgres), vagy
- használd PythonAnywhere-t hobbi célra (ott a fájlrendszer tartósabb).
