"""cocotb testbench — cycle-EXACT measurement of the RTL bus FIFO (no FPGA; runs in simulation).

Measures, at a chosen clock, the enqueue->dequeue LATENCY (in clock cycles) and the steady-state
THROUGHPUT (items/cycle), and writes bench/results/hdl-<sim>.json in the same schema the rest of
the harness uses. Because an HDL simulator evaluates every clock edge, these cycle counts are
exact — the "cocotb fidelity" the FPGA route promises, obtained entirely on the dev machine.
"""
import json
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

CLK_NS = float(os.environ.get("HDL_CLK_NS", "5.0"))     # 5 ns => 200 MHz
FREQ_HZ = 1e9 / CLK_NS


async def _reset(dut):
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def latency_and_throughput(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, units="ns").start())
    await _reset(dut)

    # ---- enqueue->dequeue latency: push one item, count cycles until it appears out ----
    dut.wr_data.value = 0xDEADBEEFCAFEF00D
    dut.wr_en.value = 1
    await RisingEdge(dut.clk)               # item accepted this edge
    dut.wr_en.value = 0
    cycles = 0
    dut.rd_en.value = 1
    # count cycles from the read request until rd_valid asserts with the right data
    while True:
        await RisingEdge(dut.clk)
        cycles += 1
        if int(dut.rd_valid.value) == 1:
            assert int(dut.rd_data.value) == 0xDEADBEEFCAFEF00D, "FIFO returned wrong data"
            break
        if cycles > 100:
            raise cocotb.result.TestFailure("no rd_valid within 100 cycles")
    dut.rd_en.value = 0
    latency_cycles = cycles
    await _reset(dut)

    # ---- steady-state throughput: keep it full and drain concurrently, count items/cycle ----
    N = 4096
    dut.wr_en.value = 1
    dut.rd_en.value = 1
    got = 0
    total = 0
    val = 1
    for _ in range(N + 64):
        dut.wr_data.value = val
        await RisingEdge(dut.clk)
        val += 1
        total += 1
        if int(dut.rd_valid.value) == 1:
            got += 1
        if got >= N:
            break
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    items_per_cycle = got / total if total else 0.0

    ns_per_hop = latency_cycles / FREQ_HZ * 1e9
    throughput_items_s = items_per_cycle * FREQ_HZ

    sim = os.environ.get("SIM", "sim")
    result = {
        "schema": "robobus-bench/1",
        "label": f"HDL simulation ({sim}) — cycle-exact, no FPGA",
        "platform": {
            "system": "HDL-sim",
            "release": "cycle-exact",
            "version": "",
            "processor": sim,
            "machine": sim,
            "cpu_brand": f"RTL @ {FREQ_HZ/1e6:.0f} MHz ({sim})",
            "cpu_count_logical": 1,
            "platform": f"cocotb/{sim} cycle-accurate simulation",
            "python_version": "n/a", "python_impl": "cocotb",
            "environment": {"virtualized": False, "simulated": True,
                            "caveat": "cycle-EXACT (simulator evaluates every edge); ns assume the "
                                      "stated clock — real silicon adds place&route Fmax limits"},
            "measurement": {"fidelity_tier": "6/7-hdl-sim (cycle-exact RTL, no hardware)",
                            "uncontrolled_noise": [],
                            "clock_mhz": FREQ_HZ / 1e6},
            "dependencies": {"available": {"cocotb": cocotb.__version__, sim: "present"},
                             "missing": {}},
        },
        "results": [
            {"group": "hdl_sim", "name": "SPSC FIFO enqueue->dequeue latency",
             "config": {"clock_mhz": FREQ_HZ / 1e6, "width_bits": 64, "depth": 16},
             "unit": "ns", "dependency": f"cocotb/{sim}", "status": "ok",
             "note": f"{latency_cycles} clock cycles, cycle-exact; = {ns_per_hop:.2f} ns @ "
                     f"{FREQ_HZ/1e6:.0f} MHz. The bus ring as RTL.",
             "metrics": {"cycles": latency_cycles, "p50_ns": ns_per_hop, "mean_ns": ns_per_hop}},
            {"group": "hdl_sim", "name": "SPSC FIFO steady-state throughput",
             "config": {"clock_mhz": FREQ_HZ / 1e6}, "unit": "items/s",
             "dependency": f"cocotb/{sim}", "status": "ok",
             "note": f"{items_per_cycle:.3f} items/cycle x {FREQ_HZ/1e6:.0f} MHz (1.0 = full rate)",
             "metrics": {"items_per_cycle": items_per_cycle, "ops_per_s": throughput_items_s}},
        ],
        "note": "Cycle-exact RTL simulation on the dev machine (cocotb + Verilator/Icarus). "
                "Formal invariants proven separately via SymbiYosys.",
    }
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "results", f"latest-hdl-{sim}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    dut._log.info(f"latency={latency_cycles} cyc ({ns_per_hop:.2f} ns) "
                  f"throughput={items_per_cycle:.3f} items/cyc -> wrote {out}")
