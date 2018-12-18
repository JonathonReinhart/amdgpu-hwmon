#!/usr/bin/env python3
# https://github.com/torvalds/linux/blob/v4.19/drivers/gpu/drm/amd/amdgpu/amdgpu_pm.c#L1315
import argparse
from sysfs import SysFsObject

def invert_map(m):
    return {v: k for k, v in m.items()}

def c2f(c):
    return (c / 100) * (212 - 32) + 32

class AmdGpuHwmon:
    def __init__(self, cardnum=0):
        self.card = SysFsObject('/sys/class/drm/card{}'.format(cardnum))
        self.hwmon = self.card.device.hwmon.hwmon1

    @property
    def temperature(self):
        """Returns the temperature in Celsius"""
        return self.hwmon.temp1_input / 1000.0

    @property
    def fan_pwm(self):
        return self.hwmon.pwm1 / self.hwmon.pwm1_max

    @fan_pwm.setter
    def fan_pwm(self, value):
        self.hwmon.pwm1 = int(value * self.hwmon.pwm1_max)

    @property
    def fan_pwm_mode(self):
        return self.hwmon.pwm1_enable

    @fan_pwm_mode.setter
    def fan_pwm_mode(self, value):
        self.hwmon.pwm1_enable = value

def pwm_level(x):
    lvl = float(x)
    if lvl < 0 or lvl > 1:
        raise ValueError("Level must be between 0.0 and 1.0")
    return lvl

mode_map = {
    'none': 0,
    'manual': 1,
    'auto': 2,
}

def parse_args():
    ap = argparse.ArgumentParser()

    grp = ap.add_mutually_exclusive_group()
    grp.add_argument('-l', '--level', metavar='LEVEL', type=pwm_level,
            help="Manually set fan speed to LEVEL [0.0 - 1.0]")
    grp.add_argument('-a', '--auto', action='store_true',
            help="Enable automatic fan speed control")

    args = ap.parse_args()
    return args

def main():
    args = parse_args()

    a = AmdGpuHwmon()

    # Set
    if args.level:
        assert not args.auto
        a.fan_pwm_mode = mode_map['manual']
        a.fan_pwm = args.level

    if args.auto:
        assert args.level is None
        a.fan_pwm_mode = mode_map['auto']


    # Show
    temp = a.temperature
    print("Temperature: {:.1f} C ({:.1f} F)".format(temp, c2f(temp)))

    mode = a.fan_pwm_mode
    print("Fan mode: {} ({})".format(mode, invert_map(mode_map).get(mode, '???')))
    print("Fan PWM: {:.02f} %".format(a.fan_pwm * 100))


if __name__ == '__main__':
    main()
