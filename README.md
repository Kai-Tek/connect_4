# Connect 4 sieciowe

Projekt gry Connect 4 pisany w Pythonie.

## Etapy pracy

1. Logika gry: plansza, ruchy, tury, zwyciestwo i remis.
2. Prosty interfejs graficzny na jednym komputerze.
3. Przeciaganie pionkow w GUI.
4. Tryb sieciowy: serwer i klient dla dwoch komputerow.
5. Menu gry i dopracowanie wygladu.

## Uruchamianie pierwszego etapu

W terminalu VS Code, bedac w folderze projektu, wpisz:

```powershell
py src/main.py
```

## Uruchamianie wersji graficznej

```powershell
py src/gui_app.py
```

W menu graficznym sa teraz trzy glowne tryby:

- `Gra lokalna` - dwie osoby graja przy jednym komputerze.
- `Hostuj gre` - ten komputer uruchamia serwer i dolacza jako gracz 1.
- `Dolacz do gry` - drugi komputer wpisuje adres IP hosta i dolacza jako gracz 2.

## Uruchamianie pierwszej wersji sieciowej

To jest tekstowa wersja testowa. Nadal jest przydatna do sprawdzania, czy siec dziala.

Na komputerze, ktory ma hostowac gre:

```powershell
py src/network_server.py
```

Na pierwszym i drugim komputerze gracza:

```powershell
py src/network_client.py ADRES_IP_SERWERA
```

Jesli testujesz wszystko na jednym komputerze, uruchom dwa osobne terminale klienta:

```powershell
py src/network_client.py 127.0.0.1
```

## Uruchamianie testow

```powershell
$env:PYTHONPATH='src'
py -m unittest discover -s tests
```
