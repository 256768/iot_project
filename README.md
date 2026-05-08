# Parking space monitoring system
A semestral project for a BPC-IOT course at BUT FEEC.
Technical description is in Czech (at least temporarily).

## Návrh technického řešení.

## Popis vaší aplikace.

## Využité komponenty.

## Volba použité přenosové technologie a zdůvodnění.

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
