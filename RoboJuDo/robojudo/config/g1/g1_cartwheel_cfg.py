from __future__ import annotations
from robojudo.config import cfg_registry
from robojudo.pipeline.pipeline_cfgs import RlMultiPolicyPipelineCfg
from robojudo.controller.ctrl_cfgs import UnitreeCtrlCfg
from robojudo.environment.env_cfgs import UnitreeEnvCfg
from .env.g1_real_env_cfg import G1RealEnvCfg
from .policy.g1_unitree_policy_cfg import G1UnitreePolicyCfg
from .policy.g1_beyondmimic_policy_cfg import G1BeyondMimicPolicyCfg

@cfg_registry.register
class g1_cartwheel(RlMultiPolicyPipelineCfg):
    '''Onboard deployment with cartwheel policy - UnitreeCppEnv with DUMMY odometry'''

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",  # C++ version for speed (50Hz stable)
        odometry_type="DUMMY",      # No sport service needed
        unitree=UnitreeEnvCfg.UnitreeCfg(
            net_if="eth0",
            robot="g1",
            msg_type="hg",
        ),
    )

    ctrl: list[UnitreeCtrlCfg] = [
        UnitreeCtrlCfg(
            triggers={
                "A": "[SHUTDOWN]",          # Emergency stop
                "Y": "[POLICY_TOGGLE]",     # Toggle locomotion ↔ cartwheel
                "X": "[MOTION_FADE_IN]",    # Start motion playback
                "B": "[MOTION_FADE_OUT]",   # Pause motion playback
            }
        ),
    ]

    # Policies list: First is default (Policy 0), rest are extra policies
    policies: list[G1UnitreePolicyCfg | G1BeyondMimicPolicyCfg] = [
        G1UnitreePolicyCfg(),  # Policy 0: Unitree locomotion
        G1BeyondMimicPolicyCfg(  # Policy 1: Cartwheel
            policy_name="g1_cartwheel",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
        ),
    ]
