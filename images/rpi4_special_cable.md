Below is the special cable that you need to make for the Raspberry Pi 4 / 400 / 5 / 500 / 500+

Since the Raspberry Pi Power and OTG port are on the same USB-C Connector, and the Blink Sync Module does not have enough current to power the Pi, the red wire inside the USB-C to USB-A cable must be cut.

An external 5V 3A power supply must be then spliced into the cable in order to power the Pi. There needs to be a common GND between all three devices.

Try not to cut the data wires in the cable in order to preserve signal integrity.

Also try to make the splice point as close as possible to the USB-C connector in order to minimise voltage drop across the quite thin wires of the USB-C to Type-A cable.
```
                                   CABLE SPLICE METHOD
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            USB-C to Type-A Cable (Modified)                              │
│                                                                                          │
│  Raspberry Pi 4                [ Cable Interior ]                Blink Sync Module 2     │
│  ┌──────────────┐                                                ┌──────────────────┐    │
│  │              │   Red (+5V)   ─────────────────────── X ───────┤ (Red wire CUT)   │    │
│  │        USB-C │════════════════════════════════════════════════┤ USB-A            │    │
│  │              │   Black (GND) ─────────────────────────────────┤                  │    │
│  │              │   Data +/-    ─────────────────────────────────┤      Micro-B     │    │
│  └──────────────┘                                                └──────────────────┘    │
│                                 ▲                                         ▲              │
│                                 │ (Spliced/Tapped into cable)             │              │
│                                 │                                         |              │
│                    ┌────────────┴──────────────────────────┐     ┌────────┴─────────┐    │
│                    │    External 5V 3A Power Supply        │     |                  |    │
│                    │                                       │     |    Sync Module   |    │
│                    │  [ +5V ] ───→ Tapped to Red Wire      │     |       PSU        |    │
│                    │  [ GND ] ───→ Tapped to Black Wire    │     │                  |    |
│                    └───────────────────────────────────────┘     └──────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────┘

Legend:
  ════ = Physical Cable Outer Jacket
  ───  = Internal Copper Wires
  X    = Wire Cut / Disconnected
  ▲    = Power Injection Point (Solder/Tap)
```

An alternative approach could be to connect the external PSU directly to the Pis pin header and use a more simply modified USB-C to Type-A Cable with just the +5V (red) internal wire CUT.

```
                              ALTERNATIVE PIN HEADER METHOD
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            USB-C to Type-A Cable (Modified)                              │
│                                                                                          │
│  Raspberry Pi 4                [ Cable Interior ]                Blink Sync Module 2     │
│  ┌──────────────┐                                                ┌──────────────────┐    │
│  │              │   Red (+5V)   ─────────────────────── X ───────┤ (Red wire CUT)   │    │
│  │        USB-C │════════════════════════════════════════════════┤ USB-A            │    │
│  │              │   Black (GND) ─────────────────────────────────┤                  │    │
│  │              │   Data +/-    ─────────────────────────────────┤      Micro-B     │    │
│  └──────────────┘                                                └──────────────────┘    │
│          ▲                                                                 ▲             │
│          │ (Connected to Pi Pin Header)                                    |             │
│          │                                                                 |             │
│  ┌───────┴───────────────────────────────┐                       ┌─────────┴────────┐    │
│  │    External 5V 3A Power Supply        │                       |                  |    │
│  │                                       │                       |   Sync Module    |    │
│  │  [ +5V ] ───→ Attached to header PIN  │                       |       PSU        |    │
│  │  [ GND ] ───→ Attached to header PIN  │                       |                  |    │
│  └───────────────────────────────────────┘                       └──────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────┘

Legend:
  ════ = Physical Cable Outer Jacket
  ───  = Internal Copper Wires
  X    = Wire Cut / Disconnected
  ▲    = Power Injection Point (Header PIN)

Do not connect the Sync Module 2 to Rapberry Pi 4/400/5/500/500+ with a non-modified cable.
```
