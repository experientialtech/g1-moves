from __future__ import annotations

from robojudo.config import cfg_registry
from robojudo.pipeline.pipeline_cfgs import RlMultiPolicyPipelineCfg
from robojudo.controller.ctrl_cfgs import KeyboardCtrlCfg, UnitreeCtrlCfg
from .env.g1_mujuco_env_cfg import G1MujocoEnvCfg
from .env.g1_real_env_cfg import G1RealEnvCfg
from .policy.g1_mjlab_policy_cfg import G1MjlabPolicyCfg


PULLOVER_FRAMES = 2125


def pullover_policy() -> G1MjlabPolicyCfg:
    return G1MjlabPolicyCfg(
        policy_name="V_PullOver_154",
        without_state_estimator=True,
        use_modelmeta_config=True,
        use_motion_from_model=True,
        max_timestep=PULLOVER_FRAMES,
        start_timestep=0,
        loop_motion=True,
        loop_start_timestep=0,
        action_beta=1.0,
    )


@cfg_registry.register
class g1_pullover_dance_real(RlMultiPolicyPipelineCfg):
    """Real Unitree G1 EDU pullover dance loop.

    Controls on Unitree controller:
    - X: start / resume the dance loop
    - B: stop / pause the dance loop
    - Y: reset to the first frame
    - A: emergency damping shutdown
    """

    robot: str = "g1"
    env: G1RealEnvCfg = G1RealEnvCfg()
    ctrl: list[UnitreeCtrlCfg] = [
        UnitreeCtrlCfg(
            triggers={
                "A": "[SHUTDOWN]",
                "X": "[MOTION_FADE_IN]",
                "B": "[MOTION_FADE_OUT]",
                "Y": "[MOTION_RESET]",
            }
        )
    ]
    policy: G1MjlabPolicyCfg = pullover_policy()
    policy_extra: list[G1MjlabPolicyCfg] = []


@cfg_registry.register
class g1_pullover_dance_sim(RlMultiPolicyPipelineCfg):
    """Mujoco smoke-test config for the same pullover dance loop."""

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers={
                "Key.esc": "[SHUTDOWN]",
                "<": "[MOTION_FADE_IN]",
                ">": "[MOTION_FADE_OUT]",
                "|": "[MOTION_RESET]",
            }
        )
    ]
    policy: G1MjlabPolicyCfg = pullover_policy()
    policy_extra: list[G1MjlabPolicyCfg] = []
