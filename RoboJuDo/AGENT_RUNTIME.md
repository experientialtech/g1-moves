# Agent Runtime Instructions: V_PullOver RoboJuDo Dance Loop

These instructions are for the Hermes/robot operator agent running the Unitree G1 EDU deployment from T2.

## Scope

Use this only for the RoboJuDo-ready 154-dim V_PullOver package in this repo. Do not substitute old `policy/*.onnx` artifacts or 160-dim policies.

Repo:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo
```

Main config:

```text
g1_pullover_dance_real
```

Sim smoke-test config:

```text
g1_pullover_dance_sim
```

## Preflight checks

Run these before telling Mitch it is ready:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo

# Verify artifacts and executable launchers.
stat assets/models/g1/mjlab/V_PullOver_154.onnx \
     assets/models/g1/mjlab/V_PullOver_154.pt \
     assets/models/g1/mjlab/V_PullOver_154.npz \
     scripts/start_pullover_dance.sh \
     scripts/stop_pullover_dance.sh

# Verify config registration and policy settings.
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
$PY - <<'CHECK'
import importlib, onnx
importlib.import_module('robojudo.config.g1.g1_pullover_dance_cfg')
from robojudo.config import cfg_registry
for name in ['g1_pullover_dance_real', 'g1_pullover_dance_sim']:
    cfg = cfg_registry.get(name)()
    assert cfg.policy.policy_name == 'V_PullOver_154'
    assert cfg.policy.without_state_estimator is True
    assert cfg.policy.use_modelmeta_config is True
    assert cfg.policy.use_motion_from_model is True
    assert cfg.policy.loop_motion is True
    assert cfg.policy.max_timestep == 2125
m = onnx.load('assets/models/g1/mjlab/V_PullOver_154.onnx')
ins = {i.name: [d.dim_value or d.dim_param for d in i.type.tensor_type.shape.dim] for i in m.graph.input}
outs = {o.name: [d.dim_value or d.dim_param for d in o.type.tensor_type.shape.dim] for o in m.graph.output}
meta = {kv.key: kv.value for kv in m.metadata_props}
assert ins['obs'][-1] == 154, ins
assert 'time_step' in ins, ins
assert outs['actions'][-1] == 29, outs
for key in ['joint_names','default_joint_pos','joint_stiffness','joint_damping','action_scale','anchor_body_name','body_names']:
    assert key in meta, key
assert meta.get('task') == 'Mjlab-Tracking-Flat-Unitree-G1-No-State-Estimation'
print('PREFLIGHT_OK')
CHECK
```

## Human safety gate

Before launching real robot control, confirm with Mitch or the onsite operator:

- G1 is physically powered, clear of people/obstacles, and has a safe fall zone.
- Robot is tethered or otherwise protected for first run.
- E-stop/damping control is physically in hand.
- Operator understands controller buttons: X start/resume, B stop/pause, Y reset, A emergency damping shutdown.

Do not start the real config just to test without this safety gate.

## Start real deployment

From T2:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo
./scripts/start_pullover_dance.sh
```

Equivalent direct command:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
$PY scripts/run_pipeline.py -c g1_pullover_dance_real
```

## Runtime controls

Real Unitree controller:

- X: start/resume the pullover dance loop.
- B: stop/pause the dance loop.
- Y: reset to frame 0.
- A: emergency damping shutdown.

The motion loops after frame 2125, about 42.5 seconds at 50 fps.

## First-run procedure

1. Start the launcher.
2. Keep robot stopped/paused initially.
3. Press Y to reset to frame 0.
4. Press X briefly, then B after about 0.5s.
5. Inspect posture/logs and verify no runaway actions.
6. Repeat for about 1s, then about 2s.
7. Only attempt a full loop after the short tests are stable.

## Stop

From another T2 shell:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo
./scripts/stop_pullover_dance.sh
```

If needed, inspect lingering processes:

```bash
pgrep -af 'scripts/run_pipeline.py -c g1_pullover_dance_real|g1_pullover_dance_real'
```

## Sim smoke test

Use only when a display/Mujoco environment is available:

```bash
cd /home/mitch/Repositories/g1-moves/RoboJuDo
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
$PY scripts/run_pipeline.py -c g1_pullover_dance_sim
```

Keyboard controls in sim:

- `<`: start/resume
- `>`: stop/pause
- `|`: reset
- Esc: shutdown

## Readiness criteria

Declare ready only if:

- ONNX input `obs` is 154 and output `actions` is 29.
- ONNX has `time_step` input and motion outputs.
- Metadata contains joint names, default joints, gains, action scales, anchor body, and body names.
- Config imports and registry lookup pass for real and sim configs.
- Launcher scripts are executable.
- Human safety gate is satisfied for real robot actuation.
