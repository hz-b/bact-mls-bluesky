from bact_mls_ophyd.devices.pp import bpm
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from bluesky.simulators import check_limits
from databroker import catalog

import bluesky.plans as bp
from cycler import cycler
import numpy as np
from functools import partial


def main():

    bpm_devs = bpm.BPM("BPMZ1X003GP", name="bpm")

    lt = LiveTable(
        [
            bpm_devs.count.name,
        ]
    )

    if not bpm_devs.connected:
        bpm_devs.wait_for_connection()
    print(bpm_devs.describe())
    data = bpm_devs.read()
    print(data["bpm_x_pos"])
    # print(bpm_devs.read())
    return

    md = dict(
        machine="MLS",
        nickname="bpm_test",
        measurement_target="read bpm data",
        target="see if bpm data can be read by RunEngine",
        comment="currently only testing if data taking works",
    )

    RE = RunEngine(md)
    RE(bp.count([bpm_devs], 5), [lt])


if __name__ == "__main__":
    main()
