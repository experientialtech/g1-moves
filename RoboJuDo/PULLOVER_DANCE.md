# V_PullOver RoboJuDo Dance Loop

This repo contains everything needed for the RoboJuDo side of the V_PullOver 154-dim G1 EDU deployment.

## Included artifacts

- `assets/models/g1/mjlab/V_PullOver_154.onnx` - self-contained policy + motion ONNX
- `assets/models/g1/mjlab/V_PullOver_154.pt` - source checkpoint copy
- `assets/models/g1/mjlab/V_PullOver_154.npz` - source motion reference
- `robojudo/config/g1/g1_pullover_dance_cfg.py` - custom real/sim configs
- `scripts/start_pullover_dance.sh` - start the real robot config
- `scripts/stop_pullover_dance.sh` - stop the launched process

## Controls

Real robot controller (`g1_pullover_dance_real`):

- `X` starts/resumes the dance loop
- `B` stops/pauses the dance loop
- `Y` resets to frame 0
- `A` emergency damping shutdown

The policy has `loop_motion=True`, `max_timestep=2125`, and `loop_start_timestep=0`, so after start it repeats the full ~42.5s dance until stopped.

## Run

Real robot:

```bash
./scripts/start_pullover_dance.sh
# or, if you want to call Python directly:
.venv/bin/python scripts/run_pipeline.py -c g1_pullover_dance_real
```

Stop the launcher process from another shell:

```bash
./scripts/stop_pullover_dance.sh
```

Sim smoke test:

```bash
.venv/bin/python scripts/run_pipeline.py -c g1_pullover_dance_sim
```

## Safety

This is a learned motion policy. First real run should be tethered, clear fall zone, E-stop in hand, and short start/stop tests before a full loop. Use only the 154-dim `V_PullOver_154.onnx` artifact for this config.

## Agent runtime instructions

See `AGENT_RUNTIME.md` for the preflight checklist, human safety gate, launch/stop commands, first-run sequence, and deploy readiness criteria.
