from robojudo.config import ASSETS_DIR
from robojudo.policy.policy_cfgs import BeyondMimicPolicyCfg
from robojudo.config.g1.env.g1_env_cfg import G1_29DoF


class G1MjlabPolicyCfg(BeyondMimicPolicyCfg):
    """Config for self-contained mjlab/G1-Moves ONNX tracking policies.

    The RoboJuDo-ready exports include:
    - actor policy input `obs`,
    - `time_step` input,
    - reference motion outputs (`joint_pos`, `joint_vel`, body states),
    - ONNX metadata for joint order, default pose, action scales, and body names.

    Use `without_state_estimator=True` for real-robot 154-dim G1 EDU policies.
    """

    robot: str = "g1"
    policy_name: str = "V_PullOver_154"

    obs_dof: G1_29DoF = G1_29DoF()
    action_dof: G1_29DoF = G1_29DoF()

    action_beta: float = 1.0
    without_state_estimator: bool = True
    override_robot_anchor_pos: bool = True

    use_modelmeta_config: bool = True
    use_motion_from_model: bool = True

    action_scales: list[float] = [0.5] * 29

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/mjlab/{self.policy_name}.onnx"
        return policy_file.as_posix()
