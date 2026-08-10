# Webseite Förderverein der Grundschule Euba e.V.

Live unter **[kinderundjugend-euba.de](https://kinderundjugend-euba.de)**

---

## Wie die Seite online geht

Der Ordner liegt in Google Drive und ist **gleichzeitig ein Git-Repository**. Gehostet wird über
GitHub Pages aus dem Repo `eubaer-web/foerderverein-euba` (Branch `main`).

Eine Änderung ist erst live, wenn sie gepusht wurde:

```bash
git add .
git commit -m "Was wurde geändert"
git push origin main
```

Danach 1–2 Minuten warten (GitHub Pages baut neu) und die Seite mit **Cmd+Shift+R** hart neu laden –
ein normaler Reload zeigt oft noch die alte Version aus dem Browser-Cache.

Die Domain hängt an der Datei `CNAME` – die bitte nicht löschen.

---

## Was wo liegt

| Datei | Zweck |
|---|---|
| `index.html` | Die komplette Website – alle Tabs stecken als Abschnitte in dieser einen Datei |
| `danke.html` | Dankeseite nach erfolgreicher Stripe-Zahlung |
| `flyer-quelle/` | Bearbeitbare Quelle der Flyer + Bau-Skript (siehe unten) |
| `flyer-foerderverein-*.pdf` | Die fertigen Flyer zum Download auf der Website |
| `vereinssatzung.pdf`, `aufnahmeantrag.docx`, `2026-01-06_…_Protokoll.doc` | Vereinsdokumente im Tab *Dokumente* |
| `logo-neu.jpeg`, `favicon.*` | Logo und Browser-Icon |

Die Tabs werden per JavaScript umgeschaltet. Ein Link auf einen bestimmten Tab funktioniert über
den Anker, z. B. `kinderundjugend-euba.de/#mitgliedschaft` – genau das steckt im QR-Code
„Mitglied werden“.

---

## Zahlungen (Stripe)

Auf der Seite sind zwei Dinge eingebunden:

- **Mitgliedschaft** – eine Stripe *Pricing Table* mit drei Jahresstufen: **6 € / 24 € / 60 €**.
  Der Abschluss des Abos *ist* die Mitgliedschaft.
- **Spende** – ein Stripe *Payment Link* für einmalige Beträge.

Aktive Zahlungsarten: **Karte, Apple Pay, Google Pay**.

Ein paar Dinge, die immer wieder für Verwirrung sorgen:

- **Apple Pay** erscheint nur in *Safari* auf iPhone/iPad/Mac mit Karte in der Wallet.
  Auf Android taucht es nie auf – das ist kein Fehler.
- **Google Pay** erscheint nur, wenn im Google Wallet des Geräts eine Karte hinterlegt ist.
- Eine **Domain-Verifizierung** ist nicht nötig, solange der Bezahlvorgang auf
  `checkout.stripe.com` läuft – also solange die Pricing Table verwendet wird.
- **SEPA-Lastschrift** *funktioniert bei Stripe auch für Abos* und wäre mit 0,35 € pauschal je
  Buchung günstiger als Karte (1,5 % + 0,25 €). Es ist bewusst nicht aktiviert, weil Stripe dafür
  eine zusätzliche Verifizierung verlangt. Es lässt sich jederzeit nachrüsten, **ohne neue Produkte
  anzulegen** – SEPA erscheint dann einfach als weitere Option im Checkout.

Mitglieder verwalten und kündigen ihr Abo selbst über das Stripe-Kundenportal. Der Link steht auf
`danke.html` und im Tab *Mitgliedschaft*; der Vorstand muss dafür nichts tun.

---

## Flyer ändern

Die Flyer entstehen aus **einer** HTML-Datei: `flyer-quelle/flyer-a5.html`.
Dort Text oder Farben anpassen, dann neu bauen:

```bash
python3 flyer-quelle/build-flyer.py
```

Das Skript erzeugt alle drei PDFs neu und prüft am Ende selbst, ob an den Rändern weiße Streifen
stehen geblieben sind (alle Werte müssen `0.00 mm` sein):

| Datei | Format | Verwendung |
|---|---|---|
| `flyer-foerderverein-a5.pdf` | 148 × 210 mm | zum Auslegen |
| `flyer-foerderverein-a4.pdf` | 210 × 297 mm | Aushang am schwarzen Brett |
| `flyer-foerderverein-a4-2fach.pdf` | 297 × 210 mm | zwei Flyer auf einem Blatt zum Ausschneiden |

Einmalig nötig: `pip3 install pypdf pypdfium2` (und ein installiertes Google Chrome).

**Achtung bei den QR-Codes:** Sie sind als Bilder fest in der HTML-Datei eingebettet. Wenn sich der
Spendenlink oder die Website-Adresse ändert, müssen die QR-Codes neu erzeugt und ausgetauscht
werden – ein reines Ändern des Textes im Flyer reicht nicht.

Warum das Skript den Umweg über `pypdf` geht statt die Seite im Browser zu skalieren: Chrome druckt
die Seite minimal größer als das CSS-Layoutfenster, wodurch am Rand ein weißer Haarstreifen stehen
bleibt. Die A4-Fassungen werden deshalb aus dem fertigen A5-PDF berechnet und der Inhalt exakt auf
das Seitenformat eingepasst.

---

## Mitglieder-E-Mails (Brevo)

Für Rundmails an die Mitglieder gibt es ein kostenloses **Brevo**-Konto
(300 Mails/Tag, unbegrenzt Kontakte, Server in der EU).
Absenderadresse `fv-gs-euba@goldmail.de` ist verifiziert.

Hinweis: Brevo pausiert neue Konten grundsätzlich und schaltet sie erst nach einer kurzen Anfrage
beim Support frei.

---

## Offene Punkte

- [ ] Brevo-Freischaltung durch den Support abwarten
- [ ] Mitglieder-Kontakte in Brevo importieren
- [ ] Info-Mail an die ehemaligen Mitglieder: Nach der Liquidation sind alle alten SEPA-Mandate
      erloschen, alle müssen sich einmalig über die Website neu anmelden
- [ ] Stripe (und Brevo) in der Datenschutzerklärung ergänzen – dort steht bisher nur GitHub Pages
- [ ] Satzungsänderungen in der Mitgliederversammlung beschließen: §3.1 elektronischer Aufnahme-
      antrag, §3.3 flexible Kündigung, §3.7 Geschäftsjahr auf Kalenderjahr
