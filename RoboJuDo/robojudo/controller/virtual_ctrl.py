"""Virtual controller for GUI-based control of RoboJuDo.

This controller receives commands from a GUI (like web buttons) and
translates them into joystick-like inputs for the robot.
"""

from typing import Optional
from robojudo.controller import Controller, ctrl_registry
from robojudo.controller.ctrl_cfgs import CtrlCfg


class VirtualCtrlCfg(CtrlCfg):
    """Configuration for virtual controller.

    Args:
        ctrl_type: Controller type name
        triggers: Dict mapping button names to trigger commands
        triggers_extra: Dict mapping button names to extra trigger commands
    """
    ctrl_type: str = "VirtualCtrl"
    triggers: dict[str, str] = {}
    triggers_extra: dict[str, str] = {}


@ctrl_registry.register
class VirtualCtrl(Controller):
    """Virtual controller that simulates joystick input from GUI commands.

    This controller maintains internal state for axes (velocity commands) and
    buttons (action triggers) that can be updated externally via GUI.
    """
    cfg_ctrl: VirtualCtrlCfg

    def __init__(self, cfg_ctrl: VirtualCtrlCfg, env=None, **kwargs):
        """Initialize virtual controller.

        Args:
            cfg_ctrl: Configuration with button trigger mappings
            env: Environment reference (optional)
        """
        super().__init__(cfg_ctrl=cfg_ctrl, env=env, **kwargs)

        # Virtual joystick axes: [vx, vy, omega]
        self.axes = [0.0, 0.0, 0.0]

        # Virtual buttons state
        self.buttons = {}
        self._button_presses = []  # Queue of button press events

    def set_axes(self, vx: float, vy: float, omega: float):
        """Set velocity command axes.

        Args:
            vx: Forward velocity (m/s)
            vy: Lateral velocity (m/s)
            omega: Angular velocity (rad/s)
        """
        self.axes = [vx, vy, omega]

    def press_button(self, button_name: str):
        """Register a button press event.

        Args:
            button_name: Name of button pressed (e.g., "A", "B", "X", "Y")
        """
        self._button_presses.append(button_name)

    def get_data(self):
        """Get current control data (required by Controller base class).

        Returns:
            Dict with velocity commands and button events
        """
        return {
            'vx': self.axes[0],
            'vy': self.axes[1],
            'omega': self.axes[2],
            'button_events': self._button_presses.copy()
        }

    def process_triggers(self, ctrl_data):
        """Process button press triggers into commands.

        Args:
            ctrl_data: Control data dict from get_data()

        Returns:
            Tuple of (ctrl_data, commands list)
        """
        commands = []
        if len(self.triggers) == 0:
            return ctrl_data, commands

        # Process button presses
        for button in ctrl_data.get('button_events', []):
            command = self.triggers.get(button, None)
            if command is not None:
                commands.append(command)

        # Clear processed button presses
        self._button_presses.clear()

        return ctrl_data, commands

    def reset(self):
        """Reset controller to initial state."""
        self.axes = [0.0, 0.0, 0.0]
        self.buttons = {}
        self._button_presses.clear()


# Global virtual controller instance
_virtual_controller: Optional[VirtualCtrl] = None


def set_virtual_controller(ctrl: VirtualCtrl):
    """Set the global virtual controller instance.

    Args:
        ctrl: VirtualCtrl instance to use globally
    """
    global _virtual_controller
    _virtual_controller = ctrl


def get_virtual_controller() -> Optional[VirtualCtrl]:
    """Get the global virtual controller instance.

    Returns:
        Current VirtualCtrl instance or None
    """
    return _virtual_controller
