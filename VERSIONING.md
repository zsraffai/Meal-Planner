# Helyi verziókezelés (Git nélkül)

Mivel ezen a gépen jelenleg nincs `git`, ideiglenesen snapshot-alapú verziókezelés van beállítva.

## 1) Új verzió mentése

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_snapshot.ps1 -Label "fix-inline-onclick"
```

Ez létrehoz egy új mentést a `.snapshots` mappába (időbélyeggel).

## 2) Elérhető verziók listázása

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\list_snapshots.ps1
```

## 3) Visszaállás egy verzióra

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restore_snapshot.ps1 -SnapshotName "20260302-153000-fix-inline-onclick"
```

A visszaállítás előtt automatikusan készül egy biztonsági mentés is: `pre-restore-...`.

---

## Ajánlott workflow

- Javítás/funkció előtt: `create_snapshot.ps1`
- Javítás/funkció után: `create_snapshot.ps1` új labellel
- Ha gond van: `restore_snapshot.ps1`

---

## Amint felkerül a Git

Átállunk commit+tag alapú verziózásra (`v1.0.0`, `v1.0.1`, stb.), ami még tisztább és megbízhatóbb visszalépést ad.
