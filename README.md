# Parking space monitoring system
A semestral project for a BPC-IOT course at BUT FEEC.
Technical description is in Czech (at least temporarily).

BPC-IOT FEKT VUT v Brně 2026

## Návrh technického řešení.
Zařízení slouží pro vzdálený monitoring volných parkovacích míst.
- Detekce vozidla: místo ultrazvukových senzorů jsou pro simulaci vjezdu a výjezdu použita tlačítka.
- Kapacita: sytém monitoruje zaplněnost v rámci nastavené kapaciti v <config.py>. Aktuální registrační značky zaparkovaných vozidel jsou ukládány do lokálního souboru <spz.txt>.
- Vizuální signalizace: Stav parkoviště (volno/obsazeno) a akce (vjezd/výjezd) jsou znázorněny pomocí tří RGB LED diod.
- Čtení RZ: při vjezdu je náhodně generována RZ (simulujeme přečtení RZ kamerou), která je následně odeslána na server a uložena.

## Popis vaší aplikace.
Aplikace je postavena na bázi stavového automatu v jazyce MicroPython, který v hlavní smyčce preiodicky kontroluje stavy tlačítek a spravuje komunikační modul.
- Inicializace: po startu aplikace inicializuje UART rozrhaní pro komunikaci s modemem BG77, nastaví APN a provede registraci do sítě s prioritou pro LTE Cat-M.
- Logika vjezdu/výjezdu: Při detekci stisku tlačítka (vjezd nebo výjezd) dojde k aktualizaci vizuální signalizace, manipulaci se seznamem SPZ v souboru <spz.txt> a okamžitému odeslání UDP datagramu na server.
- Diagnostika: nezávisle na provozu běží časovač (Timer), který periodicky spouští funkci pro vyčtení rádiových parametrů sítě (RSRP, SINR) a odesílá je jako stavovou zprávu.
- Systém využívá lokální persistenci dat, tedy po restartu pokračuje s aktuálním počtem vozidel uloženým v souboru.
  
## Využité komponenty.
HARDWARE
- Mikrokontrolér s podporou MicroPython - Raspberry Pi Pico
- Komunikační modul Quectel BG77
- 3x RGB LED dioda pro signalizaci
- 2x mikrospínač pro simulaci vjezdu a výjezdu
Vše umístěno na jedné desce.

SOFTWARE
- Knihovna <BG77.py> pro ovládání modemu pomocí AT příkazů.
- Modul <config.py> pro konfiguraci sítě a parametrů parkoviště.

## Volba použité přenosové technologie a zdůvodnění.
Pro komunikaci byla zvolena technologie NB-IoT/LTE Cat-M s využitím BG77.

Tato technologie byla zvolena z důvodů specifického umístění v podzemních garažích a absence datových rozvodů. NB-IoT nabízí vynikající průnik signálu do budov a podzemí, zatímco díky LTE Cat-M umožňujeme efektivní přenos při nízké periodě projíždějících aut (jedno auto za 5 minut).

## Volba Transportního protokolu a zdůvodnění.
Byl zvolen transportní protokol UDP s ohledem na malé množství režijních dat nutných pro přenos.
Potvrzování vybraných zpráv lze v tomto případě přenést na aplikační úroveň.

## Volba Aplikačního protokolu a zdůvodnění.
Pro komunikaci zařízení jsme zvolili vlastní komunikační protokol, abychom minimalizovali datové přenosy.

### Struktura vlastního aplikačního protokolu
```
  1 character
   +-+-+-+-+-+-+-+-+-+-+-+-+-+
   | Type  | Message Content |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+
            rest of characters
```
Obr. 1: Struktura aplikačního protokolu

```
   +-+-+-+-+-+-+-+-+-+-+-+
   | s | RSRP,SINR,cars  |
   +-+-+-+-+-+-+-+-+-+-+-+
```
Obr. 3: Formát pro stavové informace

```
   +-+-+-+-+-+-+-+-+-+-+-+
   | i/o | license plate |
   +-+-+-+-+-+-+-+-+-+-+-+
```
Obr. 2: Formát pro vjezd a výjezd vozidel

Vlastní protokol je pro čitelnost postaven na řetězci ASCII.
První znak obsahuje informaci o typu zprávy -- vjezd, odjezd či stavové informace.
Ve zbytku zprávy se nachází přenášený obsah.
Příklad formátu je v obr. 1.
V případě vjezdu nebo odjezdu (typy *i*, *o*) je v obsahové části pouze poznávaci značka vozidla, viz obr. 2.
U stavových informací se přenáší oddělené čárkami hodnoty RSRP, SINR a počet obsazených míst na parkovišti, viz obr. 3.

## Volba napájecí soustavy a zdůvodnění.
Napájení je provedeno síťovým adaptérem, napájecí soustava 230 V/50 Hz.
Zařízení bude stacionární, rozvod je již v budově zaveden.

## Ukázka fungování/výsledky
- screen ze serveru
- video ukázka funkčnosti

## Polemika nad dosaženými výsledky.
