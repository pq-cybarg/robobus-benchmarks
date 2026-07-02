#!/usr/bin/env python3
"""Build + run the cocotb cycle-exact HDL simulation of the RTL bus FIFO.

Runs under the cocotb interpreter (needs cocotb + a simulator: icarus or verilator). Emits
bench/results/hdl-<sim>.json. Pure simulation — no FPGA / no hardware.
"""
import os
import sys

PROJ = os.path.dirname(os.path.abspath(__file__))
SIM = os.environ.get("SIM", "icarus")
os.environ["SIM"] = SIM


def main() -> int:
    try:
        from cocotb_tools.runner import get_runner       # cocotb >= 2.0
    except Exception:
        try:
            from cocotb.runner import get_runner          # cocotb 1.x
        except Exception as e:
            print(f"cocotb runner unavailable ({e})", file=sys.stderr); return 77
    runner = get_runner(SIM)
    src = os.path.join(PROJ, "spsc_fifo.v")
    try:
        runner.build(verilog_sources=[src], hdl_toplevel="spsc_fifo", always=True,
                     build_dir=os.path.join(PROJ, "_sim"))
    except TypeError:
        # cocotb 2.x renamed the arg to `sources`
        runner.build(sources=[src], hdl_toplevel="spsc_fifo", always=True,
                     build_dir=os.path.join(PROJ, "_sim"))
    runner.test(hdl_toplevel="spsc_fifo", test_module="test_spsc_fifo",
                test_dir=PROJ)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
