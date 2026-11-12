`timescale 1ns / 1ps

module can_fd_ctrl (
    input  wire        clk,
    input  wire        rst_n,
    
    // APB3 Interface
    input  wire        psel,
    input  wire        penable,
    input  wire        pwrite,
    input  wire [31:0] paddr,
    input  wire [31:0] pwdata,
    output reg  [31:0] prdata,
    output reg         pready,
    
    // CAN PHY Interface
    output wire        can_tx,
    input  wire        can_rx,
    input  wire        can_rx_error, // Для симуляции ошибок на шине
    output wire        can_tx_enable
);

    // TODO: Реализация контроллера CAN FD
    // 1. APB3 декодер регистров
    // 2. TX FIFO и арбитраж
    // 3. RX FIFO и фильтрация
    // 4. Bit Timing Logic (BTL) и стаффинг
    // 5. CRC-17/21 генератор и проверка
    
    assign can_tx = 1'b1; // Recessive по умолчанию
    assign can_tx_enable = 1'b0;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prdata <= 32'h0;
            pready <= 1'b0;
        end else if (psel && penable) begin
            pready <= 1'b1;
            if (pwrite) begin
                // TODO: Запись в регистры
            end else begin
                // TODO: Чтение из регистров
                prdata <= 32'hDEADBEEF; // Заглушка для проверки чтения
            end
        end else begin
            pready <= 1'b0;
        end
    end

endmodule
