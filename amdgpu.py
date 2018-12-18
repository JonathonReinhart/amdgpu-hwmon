#!/usr/bin/env python3
# https://github.com/torvalds/linux/blob/v4.19/drivers/gpu/drm/amd/amdgpu/amdgpu_pm.c#L1315
from sysfs import SysFsObject

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



def main():
    a = AmdGpuHwmon()
    print("Temperature: {} C".format(a.temperature))

    mode = a.fan_pwm_mode
    print("Fan mode: {} ({})".format(mode, {
            0: "no fan speed control",
            1: "manual fan speed control using pwm interface",
            2: "automatic fan speed control",
        }.get(mode, "???")))
    print("Fan PWM: {:.02f} %".format(a.fan_pwm * 100))


    a.fan_pwm_mode = 1
    a.fan_pwm = 1.0


if __name__ == '__main__':
    main()
