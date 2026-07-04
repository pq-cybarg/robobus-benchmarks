"""GPU crossover — ANALYTICAL PROJECTION (no GPU hardware required).

The GPU offload benchmark trades a fixed per-dispatch cost (kernel launch + host<->device
transfer + sync) for parallel throughput, so the CPU wins below a batch-size CROSSOVER and the GPU
wins above it. On a machine with a GPU we MEASURE that (bench_gpu, via mlx/cupy/torch). Where there
is no GPU — CI VMs, and any host we want to reason about before buying silicon — we PROJECT it with
a first-order roofline model:

    swapover(device)     = dispatch_us                          # the N->0 limit (launch+sync)
    t_cpu(bytes)         = bytes / cpu_GBps
    t_gpu_resident(bytes)= dispatch_us + bytes / gpu_GBps       # data already on-device (unified, or
                                                                #   persistent buffers) — the SCALE case
    t_gpu_cold(bytes)    = dispatch_us + 2*bytes/link_GBps + bytes/gpu_GBps   # copied in+out each batch
    crossover_bytes      = dispatch / (1/cpu_GBps - 1/gpu_eff_GBps)   # smallest batch where GPU wins

This is a PROJECTION, not a measurement — it is exact only to the linear (bandwidth/launch) model and
ignores occupancy ramp, cache effects, and kernel-fusion. For CYCLE-ACCURATE projection without
hardware, run the kernel under **GPGPU-Sim / Accel-Sim** (NVIDIA SM + memory-hierarchy models) or
**MGPUSim** (AMD) — the GPU analog of the cocotb/Verilator HDL rung. This model is the roofline rung.

The Apple-M5 unified row is CALIBRATED to our on-device measurement (dispatch 204 us, crossover
~4 MiB); the discrete rows are PROJECTED from vendor spec sheets (HBM bandwidth, PCIe/NVLink, launch).
"""

# device profiles: dispatch (us), gpu mem bandwidth (GB/s), host/CPU mem bandwidth (GB/s),
# host<->device link (GB/s; None = unified memory, no copy). Sources in the note per row.
PROFILES = [
    # name, dispatch_us, gpu_GBps, cpu_GBps, link_GBps, note
    ("Apple M5 (unified memory)",        204.0, 120.0,  17.5, None,
     "CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover"),
    ("NVIDIA A100 80GB (PCIe4 x16)",       8.0, 1935.0,  40.0,  25.0,
     "PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch"),
    ("NVIDIA H100 (PCIe5 x16)",            6.0, 3350.0,  40.0,  55.0,
     "PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch"),
    ("NVIDIA H100 (NVLink)",               6.0, 3350.0,  40.0, 450.0,
     "PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch"),
    ("AMD MI250 (PCIe4 x16)",              8.0, 3200.0,  40.0,  25.0,
     "PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch"),
]


def _crossover_bytes(dispatch_us, gpu_GBps, cpu_GBps, link_GBps):
    """Smallest batch (bytes) where the GPU (incl. one dispatch) beats the CPU. Returns
    (resident_bytes, cold_bytes) — resident = data already on-device (the scale case); cold =
    copied host<->device every batch. None when the GPU never wins that mode (per-byte slower)."""
    def solve(gpu_eff):
        # dispatch_us + bytes/gpu_eff  <  bytes/cpu   ->  bytes > dispatch / (1/cpu - 1/gpu_eff)
        denom = (1.0 / cpu_GBps) - (1.0 / gpu_eff)     # GB/s^-1 == ns per byte (us*GB == ns... unit-consistent below)
        if denom <= 0:
            return None
        # dispatch_us is in us; 1/GBps is s per GB = ns per byte. Convert dispatch to ns then to bytes:
        return (dispatch_us * 1000.0) / denom          # ns / (ns/byte) = bytes
    resident = solve(gpu_GBps)
    if link_GBps is None:                              # unified: no copy, cold == resident
        cold = resident
    else:
        # cold effective GPU throughput: 1/gpu_eff = 1/gpu_GBps + 2/link (copy in + out)
        gpu_eff = 1.0 / (1.0 / gpu_GBps + 2.0 / link_GBps)
        cold = solve(gpu_eff)
    return resident, cold


def project(record):
    """Emit modeled GPU swapover + crossover rows for every device profile (no hardware needed)."""
    for name, dispatch_us, gpu_GBps, cpu_GBps, link_GBps, src in PROFILES:
        record("gpu", f"swapover — {name} (modeled)",
               {"device": name, "modeled": True, "dispatch_us": dispatch_us}, "ns",
               {"p50_ns": dispatch_us * 1000.0, "mean_ns": dispatch_us * 1000.0},
               dependency="analytical model",
               note=f"projected dispatch+sync = {dispatch_us:.0f} us. {src}")
        resident, cold = _crossover_bytes(dispatch_us, gpu_GBps, cpu_GBps, link_GBps)
        def fmt(b):
            return "never (per-byte slower)" if b is None else \
                   (f"{b/1024:.0f} KiB" if b < 1024*1024 else f"{b/1048576:.1f} MiB")
        streams = "" if resident is None else f"; ~{int(resident/1024):,} concurrent 1-KiB streams"
        record("gpu", f"crossover batch — {name} (modeled)",
               {"device": name, "modeled": True}, "bytes",
               {"crossover_bytes_resident": resident, "crossover_bytes_cold": cold,
                "gpu_GBps": gpu_GBps, "cpu_GBps": cpu_GBps, "link_GBps": link_GBps},
               dependency="analytical model",
               note=(f"GPU overtakes CPU above ~{fmt(resident)} resident / {fmt(cold)} cold "
                     f"(host<->device copy each batch){streams}. Roofline projection — see "
                     f"GPGPU-Sim/Accel-Sim for cycle-accurate. {src}"))
