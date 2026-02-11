# Physics-Based Weapon Fight Simulator + Viral Content System

## 1) High-Level Architecture

### Recommended engine and stack
- **Core simulation engine:** Custom deterministic simulation layer in **Godot 4 (2D)** or **Unity DOTS 2D/3D**.
  - For fastest viral content iteration, start with **Godot 4 2D**:
    - Lightweight setup.
    - Easy deterministic tick loop.
    - Fast video capture/export tooling.
- **Content pipeline:**
  - In-engine rendering at **1080x1920 (9:16)**.
  - FFmpeg post-processing pass for overlays and encoded Shorts/Reels exports.
- **Data layer:**
  - Weapon definitions loaded from **external JSON/YAML** (hot-reload friendly).
  - Match + telemetry events stored as JSONL/CSV for analytics and auto-caption generation.

### System modules
1. **Weapon Registry**
   - Loads weapon configurations, validates schema, and exposes weapons for selection.
2. **Match Orchestrator**
   - Accepts selected weapon pair + seed.
   - Initializes arena, entities, and simulation timeline.
3. **Physics & Combat Engine**
   - Fixed-timestep deterministic loop.
   - Handles motion, wall bounces, weapon collisions, hit detection, and damage/effect application.
4. **Effect Resolver**
   - Processes bleed/crit/stun/knockback/elemental interactions and timed status effects.
5. **Health/Durability System**
   - Tracks HP + durability degradation and breakage rules.
6. **Replay Recorder**
   - Stores full state snapshots or input/event stream for deterministic replay.
7. **Tournament Service**
   - Bracket generation, batch simulation, standings and upset detection.
8. **Viral Content Generator**
   - HUD overlays (names, HP, floating damage).
   - Final-hit slow-mo.
   - Auto title/caption/hashtags.

### Determinism strategy (non-scripted winner)
- Fixed timestep (e.g., **1/120s**).
- Seeded RNG for all random rolls (crit, proc chance, spawn offsets).
- Stable update order for entities/effects each frame.
- Integer or deterministic float handling (same engine version and platform profile for production renders).
- Winner emerges strictly from simulation state transitions.

---

## 2) Weapon Data Schema (Unlimited Expansion)

Use external config to add weapons without code changes.

```yaml
id: "katana_001"
name: "Katana"
class: "blade"
rarity: "epic"

stats:
  hp: 1200
  durability: 850
  damage: 95
  attack_speed: 1.35         # swings/sec or hit attempts/sec
  reach: 2.4                 # effective hit radius/length
  mass: 7.5
  base_velocity: 6.2
  turn_rate: 1.8

hitbox:
  shape: "capsule"          # circle/capsule/box/polygon
  width: 0.45
  length: 2.2

effects:
  crit:
    chance: 0.22
    multiplier: 1.75
  bleed:
    chance: 0.35
    dps: 18
    duration_sec: 2.5
  knockback:
    force: 7.0
  elemental:
    type: "none"
    bonus_vs:
      ice: 0.1

weaknesses:
  recovery_penalty_sec: 0.28
  durability_loss_on_hit: 5.5
  low_performance_vs:
    heavy: -0.12

ai_profile:
  aggression: 0.78
  spacing_preference: 0.62
  evade_bias: 0.31

visual:
  sprite: "weapons/katana.png"
  trail: "slash_red"
  sfx_hit: "katana_hit_03"
```

### Validation rules
- Required fields: `id`, `name`, `stats.hp`, `stats.damage`, `stats.attack_speed`, `stats.reach`, `hitbox.shape`.
- Bounds checks (e.g., attack_speed > 0, hp > 0).
- Trait conflicts handled via compatibility table.
- Versioned schema (`schema_version`) for future migration.

---

## 3) Arena Physics Logic

### Arena model
- Rectangular box (2D first; 3D optional extension).
- Example bounds: `width=24`, `height=42` world units.
- Closed environment: no exits, no external agents.

### Entity state
For each weapon at tick `t`:
- Position `p_t`
- Velocity `v_t`
- Angular orientation `θ_t`
- Angular velocity `ω_t`
- HP and durability
- Status effects list
- Cooldown timers

### Tick loop (fixed update)
1. **Integrate movement**
   - `p_{t+1} = p_t + v_t * dt`
2. **Boundary collision + reflection**
   - If crossing left/right wall: invert x component: `v.x = -v.x * restitution`
   - If crossing top/bottom wall: invert y component: `v.y = -v.y * restitution`
   - Reposition to contact boundary to avoid tunneling.
3. **Weapon collision detection**
   - Broad-phase: spatial hash/grid.
   - Narrow-phase: shape overlap (capsule-circle, box-box SAT, etc.).
4. **Combat resolution on collision**
   - Check attack timers and reach overlap.
   - Compute damage from base stats + relative velocity + traits/resistances.
   - Roll seeded RNG for crit/effects.
   - Apply knockback impulses and stun/recovery windows.
5. **Status updates**
   - Tick bleed/burn/poison DOT.
   - Expire timers.
6. **Durability degradation**
   - Per hit and passive wear over time.
   - Optional break mechanic: very low durability reduces damage/reach.
7. **End condition**
   - If any HP <= 0, stop simulation and publish winner + match stats.

### Sample damage model
`final_damage = base_damage * speed_factor * trait_mod * crit_mod * resistance_mod`

Where:
- `speed_factor = clamp(0.8, 1.4, |relative_velocity| / baseline)`
- `trait_mod` includes elemental advantage/disadvantage and class modifiers.
- `crit_mod` = crit multiplier or 1.0.

This keeps outcomes emergent and replayable while still interpretable.

---

## 4) Simulation Flow (Runtime)

1. User picks any 2 weapons from registry.
2. User picks mode:
   - Single match
   - Best-of-N
   - Tournament bracket
3. System requests/creates a seed.
4. Arena initializes random spawn positions + initial velocity vectors from seed.
5. Simulation runs:
   - Real time (1x)
   - Fast sim (2x, 4x, 8x for batch runs)
6. On each collision, combat/effects resolve via deterministic rules.
7. HP/durability bars update each tick.
8. First weapon to HP 0 loses.
9. Results package emitted:
   - Winner, TTK (time-to-kill), total hits, crit count, damage by type, peak combo, final blow metadata.

---

## 5) Tournament + Replayability

### Tournament support
- Bracket types: single elimination, double elimination, round robin.
- Batch sim service runs all matchups with configurable seed sets.
- Metrics:
  - Win rate per weapon
  - Match duration distributions
  - Upset score (lower-ranked beating higher-ranked)

### Replay system
- Save lightweight event stream:
  - seed
  - version hash
  - initial states
  - per-tick RNG calls/events
- Replay modes:
  - Normal
  - Slow-motion (0.25x)
  - Frame-step analysis

### Randomization for varied outcomes
- Different seeds produce varied trajectories/procs.
- Option: “Fair seed pack” where same seed set is applied across all weapon pairs for balanced comparisons.

---

## 6) Viral YouTube Shorts / Reels Mode

### Video format and HUD
- Render at **1080x1920 (9:16)**.
- UI elements:
  - Top-left: Weapon A name + HP + durability bar.
  - Top-right: Weapon B name + HP + durability bar.
  - Center: timer + round/match label.
  - Floating damage numbers on hit.
- Audio:
  - Hit SFX layering.
  - Bass impact on crit/final blow.

### Dramatic moments automation
- Trigger cinematic on final 10% HP or lethal hit:
  - Slow-mo to 0.2x for 1.2 sec.
  - Camera shake + vignette pulse.
  - “FINAL STRIKE” text burst.

### Auto metadata generation
- **Title template:**
  - `"{WeaponA} vs {WeaponB} ⚔️ | Who Wins?"`
- **Caption template:**
  - `"Seed {seed}. No scripts, pure sim. Did your pick win? 👀"`
- **Hashtags template:**
  - `#weaponsim #gaming #simulation #shorts #aiarena #{weaponA_tag} #{weaponB_tag}`

### Viral iteration loop
- Generate 20–100 matches/day across high-interest pairings.
- Rank clips by:
  - Damage spikes
  - Comeback probability
  - Match length sweet spot (20–45 sec)
  - Final-hit spectacle score
- Auto-publish top percentile with A/B title variants.

---

## 7) Clear Step-by-Step Execution Plan

### Phase 1 — Core MVP (Week 1)
1. Build deterministic fixed-tick arena simulation.
2. Implement wall bounce reflection + collision resolution.
3. Add 10 baseline weapons in config files.
4. Implement HP/durability, damage, crit, bleed.
5. Produce CLI + basic UI to run one match by weapon IDs + seed.

### Phase 2 — Content-Ready Build (Week 2)
1. Add 9:16 scene layout and cinematic HUD.
2. Add replay recorder + slow-motion final hit.
3. Implement export pipeline to MP4.
4. Add auto title/caption/hashtag generator.

### Phase 3 — Scale + Tournaments (Week 3)
1. Add bracket/tournament manager.
2. Add batch simulation tools and analytics dashboards.
3. Add weapon balancing metrics and anomaly detection.
4. Introduce schema tooling for one-click weapon imports.

### Phase 4 — Optimization + Growth (Week 4+)
1. Add advanced effects (stun chains, armor break, elemental stacks).
2. Add 3D mode variant.
3. Build creator dashboard for trend-based matchup suggestions.
4. Continuous posting loop with retention-driven clip scoring.

---

## 8) Why this meets your constraints
- **Deterministic logic:** fixed timestep + seeded RNG + stable update order.
- **No scripted winners:** result emerges from physics + combat equations only.
- **Replayability:** seed variation, expansive weapon config, tournaments.
- **Content generation optimized:** integrated 9:16 output, cinematic moments, and metadata automation.
