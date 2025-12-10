# Steam Throttle Design - Project Overview

**Date:** December 2025  
**Status:** Ideation & Requirements Gathering  
**Scope:** Handheld wireless DCC throttle emulating prototype steam locomotive control stand

## Vision

Create a functional, durable, immersive handheld DCC throttle that:
- Emulates realistic steam locomotive control stand operation
- Provides cab-relative audio feedback via Bluetooth headphones
- Enables advanced operational modes (load-aware sound, environmental context, future physics simulation)
- Serves as both operational device and training tool

## Design Principles

- **Anything worth doing is worth overdoing** — Build for durability and detail accuracy
- **Phased implementation** — Validate each phase before committing to next
- **Leverage existing infrastructure** — JMRI, MQTT, M4 mini hub, roster management
- **Iterate locally** — All fabrication (PCB, mechanical parts) done on-site with CNC/3D printers
- **Mirror prototype reality** — Control layout, feel, and operation reflect actual steam locomotives

---

## Phase 0: Validation & Learning

### CNC Validation
- Goal: Prove PCB milling workflow on Genmitsu 4030 ProVerXL2
- Task: Cut PCB ties (already planned)
- Outcome: Confidence in PCB fabrication for throttle prototype

### Operational Research
- **Age of Steam Roundhouse visit (June 2025)**
  - Hands-on training on actual steam locomotive operation
  - Learn throttle bar arc, resistance, detent feel
  - Understand brake valve operation (continuous vs. notched)
  - Understand reverser/cutoff relationship and operation
  - Understand feedwater pump and stoker manual control
  - Gather data on operator workflow and muscle memory

---

## Phase 1: Core Throttle (MVP)

### Mechanical Design

**Form Factor:**
- Single unified handheld device, ~ProtoThrottle size (7.6" × 3.2" × 3")
- Neck strap for dangling operation during layout sessions
- 3D-printed tough resin or ABS enclosure
- Metal levers/controls for durability and authentic feel

**Right Side (Engineer Controls):**
- **Throttle bar** — Metal lever in arc motion, potentiometer/encoder input
  - Continuous analog control (not discrete notches like diesel)
  - Angle/resistance TBD after Age of Steam visit
  - Smooth operation, possible tactile detents
- **Brake valve** — Metal rotary control
  - Continuous operation (assumed, to be confirmed)
  - Independent of throttle (can brake while throttled)
- **Reverser wheel** — Rotary control
  - 3-position minimum (forward/neutral/reverse)
  - Power reverse (post-1920 standard for large locos)
  - May control cutoff in future phases
- **Feedwater pump** — Rotary control (auxiliary)
- **Stoker** — Rotary control (auxiliary)
- **Bell** — Momentary push-button
- **Whistle** — Momentary spring-return button
- **Lights** — Rotary or toggle (headlight, cab lights)

**Left Side (Fireman/UI):**
- **Touchscreen LCD** — 2.4-3.5" capacitive touch
  - Roster selection (scrollable list from JMRI)
  - Locomotive information display
  - Configuration UI (WiFi, IP, WiThrottle settings)
  - Direct address entry for non-roster locos

### Electrical Design

**Core Components:**
- **Processor:** ESP32 (dual-core, WiFi, sufficient headroom)
- **Display:** Capacitive touchscreen with driver IC
- **Input devices:**
  - Potentiometers (throttle, brake, reverser, feedwater, stoker)
  - Momentary switches (bell, whistle, lights)
  - Rotary encoders (alternative to pots, if needed)
- **Power:** Rechargeable LiPo battery + USB-C charging
  - Estimated run time: TBD (typical WiFi throttle: 6-8 hours)
- **PCB:** Custom design, milled on Genmitsu CNC
  - Single-layer or two-layer FR4
  - Manhattan-style wiring acceptable for Q=1
  - Plated vias or wire jumpers for via strategy
  - Careful trace width for power rails

**Connectivity:**
- WiFi (ESP32 built-in)
- WiThrottle protocol to JMRI
- Battery powered, no tether

### Software Architecture

**ESP32 Firmware:**
- WiThrottle client (using existing Arduino library)
- Touchscreen UI driver
- Control input scanning (potentiometer ADC, switch debouncing)
- Simple mapping: throttle position → speed command, buttons → DCC functions
- JMRI roster download and caching on startup
- Configuration UI (WiFi SSID/password, IP address)

**DCC Function Mapping (Phase 1 — Basics Only):**
- F0: Headlight (on/off or dimmed)
- F1: Bell
- F2: Whistle
- F3: Cab lights (if separate function)
- *Stoker and feedwater pump deferred to phase 2*

**No feedback from decoder in phase 1** — Throttle position is the operator's feedback. Momentum/braking handled by decoder CV settings.

### Fabrication

**Enclosure:**
- 3D printed in tough resin or ABS
- Iterative design in FreeCAD
- Print, test, refine

**Metal Controls:**
- Throttle lever: CNC machined brass or aluminum, OR outsourced to sendcutsend.com for steel if needed
- Brake lever: Similar approach
- Reverser wheel: CNC machined, 2-3" diameter
- All rotary controls: potentiometers with knobs (off-the-shelf)

**PCB:**
- Design in KiCad
- Mill on Genmitsu (isolation routing, via strategy TBD)
- Hand-assemble (Q=1)

### Success Metrics (Phase 1)
- ✅ Throttle reliably connects to JMRI via WiThrottle
- ✅ Physical controls map intuitively to locomotive operation
- ✅ Enclosure is durable (survives typical drops/handling)
- ✅ Operation feels "right" — controls have weight and resistance
- ✅ Roster selection is smooth and reliable
- ✅ Can operate multiple locomotive types (different decoders)

---

## Phase 2: Audio & Telemetry

### Goals
- Implement load-aware audio synthesis
- Enable RailCom feedback from TCS decoders
- Cab-relative sound to operator via Bluetooth headphones

### Architecture

**Data Flow:**
1. Throttle sends control inputs via WiThrottle to JMRI
2. JMRI sends DCC to command station + TCS decoders
3. TCS decoders report back via RailCom:
   - Back-EMF (actual wheel speed)
   - Load current (if supported by decoder model)
4. JMRI aggregates RailCom data + block detector current measurements
5. Throttle subscribes to MQTT topics for:
   - Throttle's selected loco address
   - Back-EMF speed data
   - Block current data (load)
6. M4 mini synthesizes audio based on throttle position + actual load + back-EMF
7. Audio streamed back to throttle via Bluetooth, output to operator's headphones

**Audio Synthesis (M4 Mini):**
- Real-time parametric synthesis of steam locomotive exhaust sound
- Parameters:
  - Throttle notch (commanded power)
  - Back-EMF (actual speed)
  - Block current (actual load/effort)
  - Cutoff position (if reverser exposes it)
- Output: Continuous Bluetooth audio stream to throttle headphones
- Latency: Target <100ms for responsiveness

**RailCom Implementation:**
- Requires TCS decoders with RailCom support (most current TCS models qualify)
- Enable via CV 28/CV 29 configuration
- Command station must support RailCom cutout (NCE, TCS CS-105, etc.)
- Data reported: Address, speed (back-EMF), load (decoder-dependent)
- Note: TCS supports standard NMRA RailCom, not proprietary ESU RailCom+

### Decoder Strategy

**Roster-Aware Firmware:**
- Throttle queries JMRI for loco specifications when address selected
- Adapter code based on decoder type/capabilities
- If TCS with RailCom load reporting: use full telemetry
- If TCS with back-EMF only: use speed data only
- If non-RailCom decoder: fallback to simple throttle-position-based audio
- Support consist operation (multiple locos in consist)

### Touchscreen Enhancements

**Display Options (Future):**
- Current boiler pressure gauge (from simulated or decoder-reported load)
- Water level indicator
- Air pressure gauge (brake system)
- *Deferred to phase 3 if worthwhile*

### Success Metrics (Phase 2)
- ✅ RailCom data flows reliably from decoder through JMRI to throttle
- ✅ Audio synthesis responds in real-time to load changes
- ✅ Cab-relative audio via Bluetooth headphones is immersive
- ✅ Load-aware sound makes locomotive operation feel more prototypical

---

## Phase 3: Context & Simulation (Future)

### Environmental Context Awareness

**Indoor Localization:**
- Fixed BLE or WiFi beacons in layout room
- Mobile receiver on throttle estimates position via RSSI triangulation
- Accuracy: 1-5 meters (sufficient for zone-based audio)
- Maps to layout zones: tunnel, bridge, city, farmland, etc.
- Audio synthesis modulates ambient sound based on zone

**Use Cases:**
- Tunnel: Add echo/reverberation to exhaust sound
- Bridge: Wind noise, different acoustic environment
- City: Ambient street sounds
- Upgrade path: More granular localization for automated spotting (requires UWB or dense beacon coverage)

### Boiler Physics Simulation

**Simplified Model (Single ESP32 Core):**
- State variables: boiler_pressure, water_level
- Dynamics:
  - Pressure rises with stoker input, falls with throttle load
  - Pressure affected by cutoff (longer cutoff = faster pressure loss)
  - Water level rises with feedwater pump, falls with evaporation (proportional to throttle)
  - Throttle responsiveness modulated by boiler pressure
- Update rate: ~10 Hz
- Output: Modified DCC speed commands, throttle "feel" feedback

**Operational Impact:**
- Operator pulls throttle too hard without stoker → pressure drops → throttle becomes less responsive
- Operator must manage stoker and feedwater to maintain pressure
- Stalling possible (pressure too low for throttle to overcome load)
- Encourages prototypical operating technique

**Implementation:**
- Runs on free ESP32 core in throttle, OR on M4 mini
- Consumes <5% of available compute
- Graceful degradation: can disable if testing reveals it's not valuable

### Decoder Customization (Future)

**Consider but Don't Build in Phase 1:**
- Custom decoder firmware that reports additional telemetry
- Trade-off: Significant work vs. marginal gain (TCS decoders already good)
- Revisit only if standard decoders are limiting

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Throttle (ESP32)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ WiThrottle Client                                    │   │
│  │ Control Input Handler (pots, buttons, encoders)      │   │
│  │ Touchscreen UI (roster, config)                      │   │
│  │ [Phase 3: Boiler simulation on free core]            │   │
│  │ [Phase 2: MQTT subscriber for telemetry]             │   │
│  │ [Phase 2: Bluetooth audio output]                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  Battery + USB-C Charging                                   │
└────────────┬─────────────────────────────────────────────────┘
             │
             │ WiFi / WiThrottle
             ▼
┌─────────────────────────────────────────────────────────────┐
│              M4 Mini (Layout Control Hub)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ JMRI (DCC System, Roster, WiThrottle Server)         │   │
│  │ MQTT Broker                                          │   │
│  │ [Phase 2: Audio Synthesis Engine]                    │   │
│  │ [Phase 3: Localization Aggregator]                   │   │
│  │ [Phase 3: Physics Simulation (if M4-hosted)]         │   │
│  └──────────────────────────────────────────────────────┘   │
│  DCC Command Station Interface                              │
└────────────┬──────────────┬─────────────────────────────────┘
             │              │
             │ DCC          │ MQTT
             ▼              ▼
        ┌─────────┐   ┌──────────────┐
        │ Command │   │ Block        │
        │ Station │   │ Detectors    │
        └────┬────┘   └──────────────┘
             │
             │ DCC Track Power
             ▼
        ┌─────────────┐
        │ Locomotives │
        │ (TCS        │
        │  Decoders)  │
        └─────┬───────┘
              │ RailCom
              ▼
         [Back to Command Station]
```

---

## Known Unknowns / TBD

**Mechanical:**
- [ ] Throttle bar arc angle (learn at Age of Steam)
- [ ] Throttle bar resistance/stiffness (learn at Age of Steam)
- [ ] Brake valve operation details (continuous vs. notched)
- [ ] Reverser wheel size and operation
- [ ] Exact dimensions of all levers/controls

**Electrical:**
- [ ] Exact battery capacity and runtime estimates
- [ ] PCB layout strategy (isolation routing details, via size)
- [ ] Touchscreen selection (which model, driver, resolution trade-offs)
- [ ] Power consumption under WiFi load

**Software:**
- [ ] Exact ESP32 code structure for input sampling and WiThrottle mapping
- [ ] Touchscreen UI framework (LVGL? Custom?)
- [ ] Audio synthesis algorithm details (Phase 2)
- [ ] Localization algorithm and beacon placement (Phase 3)

---

## Timeline & Dependencies

**Immediate (Dec 2025 - Jan 2026):**
- CNC validation with PCB ties
- Age of Steam visit (June 2025 or sooner if possible)

**Near-term (Jan - Mar 2026):**
- FreeCAD mechanical design
- KiCad PCB design
- ESP32 code skeleton (dust off existing WiThrottle code)
- 3D print enclosure prototypes

**Medium-term (Apr - Jun 2026):**
- PCB fabrication and assembly
- Control integration and testing
- JMRI integration testing
- Field testing on layout

**Phase 2 (Summer 2026+):**
- Audio synthesis implementation
- RailCom integration and testing
- Bluetooth audio streaming

**Phase 3 & Beyond:**
- Context awareness features
- Physics simulation (if deemed worthwhile)
- Automated spotting/coupling support

---

## Resources & References

**Existing Infrastructure:**
- M4 mini running JMRI, MQTT broker
- Genmitsu 4030 ProVerXL2 CNC router
- AnyCubic M7 Max/Pro resin printers
- xTool S1 40W laser cutter
- FreeCAD for mechanical design

**Decoder Specifications:**
- TCS RailCom support: https://docs.tcsdcc.com/wiki/Support_-_RailCom
- NMRA RailCom standard: RP 9.3.1 and 9.3.2

**Software:**
- Arduino WiThrottle library
- ESP32 IDF or Arduino framework
- LVGL (touchscreen UI framework)

**Reference Projects:**
- ProtoThrottle (Iowa Scaled Engineering) — commercial handheld throttle
- JMRI documentation: https://www.jmri.org/

---

## Notes

- This project serves dual purpose: operational device AND training tool
- Phased approach allows proving concepts incrementally
- All fabrication local → fast iteration
- Decoder roster integration enables adaptive firmware behavior
- Future phases (audio, simulation) are genuinely valuable but independent of core throttle
- Consider building throttle first, adding features as value becomes clear

---

*Last updated: December 2025*
