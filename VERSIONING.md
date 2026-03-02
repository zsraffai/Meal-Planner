# Stabil verziózás és visszaállás (Git)

Ez a projekt most már Git-alapú stabil verziózást használ.

Alapértelmezetten a stabil mentés végén automatikusan fel is pusholja a változásokat GitHubra.

## Gyors használat (neked ez kell)

### 1) Stabil verzió mentése (minden sikeres javítás/funkció után)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_stable_version.ps1 -Label "rovid-leiras"
```

Példa:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_stable_version.ps1 -Label "login-fix"
```

Ha valamiért most nem szeretnél pusholni (csak helyi mentés):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_stable_version.ps1 -Label "local-only" -NoPush
```

### 2) Stabil verziók listázása

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\list_stable_versions.ps1
```

### 3) Visszaállás az előző stabil verzióra

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\rollback_stable.ps1
```

Alapból a `stable-previous` verzióra áll vissza.

Ha a legutóbbi stabilra akarsz visszaállni:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\rollback_stable.ps1 -Target stable-latest
```

## Mit csinál automatikusan

- Minden stabil mentésnél commit készül (ha van változás).
- Létrejön egy egyedi stabil tag: `stable-YYYYMMDD-HHMMSS-label`.
- A `stable-latest` mindig a legutóbbi stabilra mutat.
- A `stable-previous` az azelőtti stabilra mutat.
- A commit és a stabil tagek automatikusan pusholódnak a beállított remote-ra.
- Rollback előtt automatikusan készül egy biztonsági tag: `backup-before-rollback-...`.

## Ajánlott rutin

1. Módosítások után tesztelj.
2. Ha jó: `create_stable_version.ps1`.
3. Ha bármi gond: `rollback_stable.ps1`.
