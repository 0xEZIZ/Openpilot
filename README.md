# 🏴‍☠️ ADU OpenPilot | Ösen Awtoulag Hakerligi we CAN Protokol Guraly

<div align="center">
  <img src="logo (2).jpg" alt="ADU OpenPilot Logo" width="200"/>
  
  **Awtoulag kiberhowpsuzlygy, aralaşmak synaglary (pentesting), CAN torüna hüjüm we ulaglaryň yzyna inženerligi (Reverse Engineering) üçin niýetlenen, agressiw we Red Team gönükdirilen gural toplumy.**
</div>

## 📌 Gysgaça Syn (Overview)
**ADU OpenPilot** - bu **Awtoulag Red Teaming, Black-box (Gara guty) Barlaglary we CAN Protokolyny Ele Almak (Exploitation)** üçin ösdürilip ýetişdirilen ýöriteleşdirilen platformadyr. Kiberhowpsuzlyk barlagçylaryna we hakerlere häzirki zaman awtoulag torlaryny diňlemäge, okap bilmäge we OBD-II porty ýa-da içki özen CAN hatarlary arkaly dolandyryş paketlerini (Rul, Gaz, Tormoz) zor bilen siňdirmäge (Payload Injection) rugsat berýär.

**Toyota, Honda, Hyundai, Subaru, we Nissan** ýaly uly öndürijiler üçin gurlan "parser" (okaýjy logikalar) we weýran edilen `.dbc` faýllaryň uly arhiwi bilen, bu gural awtoulag torlaryndaky gowşaklyklary (vulnerabilities) ýüze çykarmak we ýapyk protokollary öwrenmek niýeti bilen taýýarlandy. Diňe arassa awtoulag kiber-toparlary üçin!

---

## ⚡ Red Team Aýratynlyklary (Hüjüm Wektorlary)
- 💉 **Işjeň Tarp (Payload) Inýeksiýasy:** Awtoulagyň esasy dolandyryş bloklaryny (ECU) bökäp geçmek arkaly ulgama göni rulyň burçuny, özboluşly torque tizligini we gaz/tormoz welaýatlaryny siňdirmek.
- 📡 **CAN Trafik Diňlemek & Gözegçilik:** Ulag öndürijiniň hakyky wagtda ugradýan hususy paketlerini berk içki `.dbc` motory arkaly "on the fly" (dessine) açyp okamak.
- 🔧 **Apparat Garaşsyzlygy we Gizlin Köprüler:** 
  - Yokary hilli ylmy barlaglar üçin **IXXAT USB-to-CAN** adapterleri bilen doly sinhron.
  - Elýeterli, arzan we uzakda ornaşdyryp (implant) bolýan **ESP32 & MCP2515** CAN köprülerini (repository-da `.ino` payload'lary goşulan) covert operasiýalary üçin goldaýar.
- 🛡️ **Gorag Gatlagy Analizi (Safety Layer Bypass):** Häzirki zaman ADAS (Ulagy sürüjäsiz dolandyrma ulgamlary) çäklendirmelerini öwrenmek, emulýasiýa etmek we olary aýlanyp geçmegiň (bypass) ýollaryny açmak üçin gurulan içki `safety_layer.py` moduly.
- 🚦 **Real-wagtda Ulagy Tabyn Etmek (Domination):** 4 tigiriň ölçeglerini onlaýn görmek we fiziki çäklendirmeleri C2 (Command & Control) edaralyk interfeýsden göni el astynda saklamak.

---

## 📁 Hakerlik Toplumynyň Gurluşy (Architecture)
```text
ADU_OpenPilot/
 ├── main.py              ← Guralyň esasy ýadrosy / Ýükleýji ekeran
 ├── gui.py               ← C2 (Command & Control) Dolandyryş Paneli
 ├── can_interface.py     ← Apparat köprülerini birikdiriji (IXXAT / Serial)
 ├── can_parser.py        ← Umumy CAN trafik diňleýji (Sniffer & Decoder)
 ├── toyota_parser.py     ← Toyota awtoulaglarynyň kodlarynyň deşifratory
 ├── toyota_commands.py   ← Exploitation Payload'lary (Rul gysymlary, Gaz)
 ├── safety_layer.py      ← Parametr çäklendirmeleri we emulýator limitleri
 ├── esp32_can_bridge.ino ← Içerki mikro-kontroller gizlin firmwary (implant)
 └── dbc_files/           ← 30+ Deşifirlenen awto-protokol bazalary (Esasy Baýlyk)
```

---

## 🛠️ Ýaraglandyryş we Gurnama

### Talap Edilmeler (Prerequisites)
Guraly operasiýa laptop-yňyza gurnamak üçin (Python 3.10+ maslahat berilýär):
```bash
pip install -r requirements.txt
# Esasy talaplar: python-can, cantools, pillow
```

### Işe Başlamak (Execution)
1. Öz CAN interfeýsiňizi (IXXAT ýa-da gizlin ESP32) awtoulagyň CAN-H we CAN-L çyzyklaryna birikdiriň.
2. C2 (Command & Control) panelini işlediň:
```bash
# Apparat bilen işjeň baglanyşyk (Real Hacking Mode)
python main.py

# Daşary analiz we tanyşlyk (Simulýasiýa we Taýýarlyk - Demo mod)
python main.py --demo
```

### Janly Dolandyryş (Emulated Controls)
Awtoulagyň gowşak CAN toryna birikdirilen wagty we sistemalar tabyn edilende:
- **Ruly Ele Almak (Steering Takeover):** `◀◀` we `▶▶` oklary ýa-da slider arkaly göni dereje (`-1500` -den `+1500` torque) sargydy.
- **Gaz/Ýokaryk Gezmek (Throttle Override):** `▲` we `▼` arkaly (-3.5 ~ +2.0 awtokonsentrat) diýdimsoňlyk güýç geçirişi amala aşyrmak.

---

## ⚠️ Kanun we Howpsuzlyk Duýduryşy (Hökman Okaň!)
> **DIŇE YLMY-BARLAG WE RUGSAT EDILEN SYNAGLAR ÜÇIN (PENTESTING).**
> Bu programma, **dine rugsat berlen ulaglarda** we kanuny tehniki platformalarda işleýän kiberhowpsuzlyk işgärleri, red-team topary we barlagçylar üçin berilýär.
> 
> **DUÝDURYŞ:** Hereket edýän maşynyň CAN toruna we çyzyklaryna göni aralaşyp paket siňdirmek **örän howpludyr**, janyňyza, maşyna ýa daş-töwerekdäkilere howp salyp biler hem-de hardware-y ugrukdyryp biler. Bu guraly açyk ýollarda, köçelerde ýa-da siziň eýeçilik etmeýän, rugsatnama alynmadyk hakyky ulaglaryňyzda **ASLA ULANMAŇ**. 
> 
> Bu taslamany dörediji ýa-da onuň proýektine goşant goşujylar, repository-nýn eýesi islendik jenaýat, zyýan, adam ölüm-ýitgisi, synag mahaly heläkçilik, ahlaksyz ulanmak we emlägiň ýitmegi babatda kanuny taýdan **hiç hili jogapkärçilik çekmeýär**. Guraly öz paýhasyňyz we jogapkärçiligiňiz astynda, ýapyk we dolandyrylýan meýdançalarda ulanyň.

---

**© 2026 ADU OpenPilot Development. Ähli hukuklar goralan.**
