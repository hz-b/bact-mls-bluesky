import matplotlib
# matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from bact_mls_ophyd.devices.pp import bpm, quadrupoles
from bact_mls_ophyd.devices.raw import tune
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from bluesky.simulators import check_limits
from databroker import catalog

import bluesky.plans as bp
from cycler import cycler
import numpy as np
from functools import partial


# Here that should be replaced
# from bact2.bluesky.live_plot import line_index, bpm_plot, orbit_plots
# from bact2.ophyd.utils.preprocessors.CounterSink import CounterSink


def main():

    bpm_devs = bpm.BPM("BPMZ1X003GP", name="bpm")
    return

    qc = quadrupoles.QuadrupolesCollection(name="qc")
    tn = tune.Tunes("TUNEZRP", name="tn")
    # cs = CounterSink(name="cs")
    
    quad_names = qc.power_converter_names.get()
    # Configure power converters to only ramp a small part
    for name in quad_names:
        quad = getattr(qc.power_converters, name)
        # use current currents as offsets
        quad.configure(dict(slope=1.0, offset=quad.r.setpoint.get()))
        print(quad.slope)

    lt = LiveTable(
        [
            qc.sel.selected.name,
            "qc_sel_p_setpoint",
            "qc_sel_r_setpoint",
            "qc_sel_p_readback",
            "qc_sel_r_readback",
            bpm_devs.count.name,
            cs.name,            
            tn.x.freq.name,
            tn.y.freq.name,
        ],
        default_prec = 10
    )
    
    lp = orbit_plots.plots(magnet_name=qc.sel.selected.name,
                           ds=bpm_devs.ds.name,
                           #ds = bpm_devs.x.pos_raw.name,
                           x_pos=bpm_devs.x.pos.name,
                           y_pos=bpm_devs.y.pos.name,
                           reading_count=cs.setpoint.name,
    )

    if not qc.connected:
        qc.wait_for_connection()
    print(qc.describe())

    cyc_magnets = cycler(qc, quad_names)
    currents = np.array([0, -1, 0, 1, 0]) * 5e-1
    cyc_currents = cycler(qc.sel, currents)
    cyc_count = cycler(cs, range(3))
    cmd = partial(bp.scan_nd, [bpm_devs, tn], cyc_magnets * cyc_currents * cyc_count)
    check_limits(cmd())

    cbs = [lt] +lp

    db = catalog["heavy"]

    md = dict(machine="MLS", nickname="bba", measurement_target="beam_based_alignment", target="beam based alignemnt test",
              comment="currently only testing if data taking works"
    )
    RE = RunEngine(md)
    RE.subscribe(db.v1.insert)
    uids = RE(cmd(), cbs)
    print(f"Measurement uid {uids}")


if __name__ == "__main__":
    plt.ion()
    try:
        main()
    except:
        raise
    else:
        plt.ioff()
        plt.show()
