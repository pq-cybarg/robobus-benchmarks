// spsc_fifo.v — the robobus ring as synthesizable RTL: a single-producer/single-consumer FIFO.
// Cycle-exact-simulated by cocotb (Verilator/Icarus) and formally verified by SymbiYosys — the
// "cocotb/FPGA fidelity without hardware" path. One item/cycle steady-state; parameterizable.
`timescale 1ns/1ps
`default_nettype none
module spsc_fifo #(
    parameter W     = 64,   // payload width
    parameter DEPTH = 16,   // must be a power of two
    parameter AW    = 4     // log2(DEPTH)
) (
    input  wire            clk,
    input  wire            rst,
    // producer
    input  wire            wr_en,
    input  wire [W-1:0]    wr_data,
    output wire            full,
    // consumer
    input  wire            rd_en,
    output reg  [W-1:0]    rd_data,
    output wire            empty,
    output reg             rd_valid
);
    reg [W-1:0]  mem [0:DEPTH-1];
    reg [AW:0]   wptr, rptr;            // one extra bit to distinguish full from empty
    wire [AW-1:0] waddr = wptr[AW-1:0];
    wire [AW-1:0] raddr = rptr[AW-1:0];

    assign full  = (wptr[AW] != rptr[AW]) && (waddr == raddr);
    assign empty = (wptr == rptr);

    always @(posedge clk) begin
        if (rst) begin
            wptr     <= 0;
            rptr     <= 0;
            rd_valid <= 1'b0;
        end else begin
            rd_valid <= 1'b0;
            if (wr_en && !full) begin
                mem[waddr] <= wr_data;
                wptr       <= wptr + 1'b1;
            end
            if (rd_en && !empty) begin
                rd_data  <= mem[raddr];
                rptr     <= rptr + 1'b1;
                rd_valid <= 1'b1;
            end
        end
    end

`ifdef FORMAL
    // constrain the formal initial state to a valid (empty) FIFO; the invariants are then
    // inductive: writes only when !full, reads only when !empty, so count stays in [0,DEPTH].
    initial assume (wptr == 0 && rptr == 0);
    wire [AW:0] count = wptr - rptr;
    always @(posedge clk) begin
        assert (count <= DEPTH);              // never overflow
        assert (!(full && empty));            // never both full and empty
        if (empty) assert (count == 0);
        if (full)  assert (count == DEPTH);
    end
`endif
endmodule
`default_nettype wire
