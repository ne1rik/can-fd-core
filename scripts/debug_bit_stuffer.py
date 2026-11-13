#!/usr/bin/env python3
"""
Пошаговая симуляция бит-стаффинга для отладки.
Эмулирует логику модуля bit_stuffer.sv такт за тактом.
"""

class BitStufferSimulator:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.first_bit = 1
        self.consecutive_count = 0
        self.last_bit = 0
        self.need_stuff_bit = 0
        self.stuff_count = 0
        self.data_out = 1
        self.data_out_valid = 0
    
    def tick(self, data_in, data_in_valid):
        """Один такт работы модуля"""
        old_state = {
            'first_bit': self.first_bit,
            'consecutive_count': self.consecutive_count,
            'last_bit': self.last_bit,
            'need_stuff_bit': self.need_stuff_bit,
            'stuff_count': self.stuff_count,
            'data_out': self.data_out,
            'data_out_valid': self.data_out_valid
        }
        
        # Логика модуля (порядок приоритетов как в RTL)
        if self.need_stuff_bit:
            # Вставляем инвертированный бит
            self.data_out = 1 - self.last_bit
            self.data_out_valid = 1
            self.stuff_count += 1
            self.consecutive_count = 1
            self.last_bit = 1 - self.last_bit
            self.need_stuff_bit = 0
        elif data_in_valid:
            self.data_out = data_in
            self.data_out_valid = 1
            
            if self.first_bit:
                self.last_bit = data_in
                self.consecutive_count = 1
                self.first_bit = 0
            elif data_in == self.last_bit:
                self.consecutive_count += 1
                # ВАЖНО: проверяем ДО инкремента!
                if self.consecutive_count == 5:
                    self.need_stuff_bit = 1
            else:
                self.consecutive_count = 1
                self.last_bit = data_in
        else:
            self.data_out_valid = 0
        
        return old_state


# Тест: 5 единиц подряд
sim = BitStufferSimulator()
print("=== Тест: 5 единиц подряд ===\n")
print(f"{'Такт':<6} {'data_in':<8} {'valid':<6} {'consec':<7} {'last':<5} {'need':<5} {'stuff':<6} {'out':<4} {'out_v':<6}")
print("-" * 70)

# Сброс
for tick in range(3):
    old = sim.tick(0, 0)
    print(f"{tick:<6} {'-':<8} {'-':<6} {old['consecutive_count']:<7} {old['last_bit']:<5} {old['need_stuff_bit']:<5} {old['stuff_count']:<6} {old['data_out']:<4} {old['data_out_valid']:<6}")

# Подаём 5 единиц
for tick in range(3, 8):
    old = sim.tick(1, 1)
    print(f"{tick:<6} {1:<8} {1:<6} {old['consecutive_count']:<7} {old['last_bit']:<5} {old['need_stuff_bit']:<5} {old['stuff_count']:<6} {old['data_out']:<4} {old['data_out_valid']:<6}")

# Ждём вставку стафф-бита
for tick in range(8, 11):
    old = sim.tick(0, 0)
    print(f"{tick:<6} {'-':<8} {'-':<6} {old['consecutive_count']:<7} {old['last_bit']:<5} {old['need_stuff_bit']:<5} {old['stuff_count']:<6} {old['data_out']:<4} {old['data_out_valid']:<6}")

print(f"\nФинальный stuff_count: {sim.stuff_count}")
print(f"Ожидалось: 1")
print(f"Результат: {'PASS' if sim.stuff_count == 1 else 'FAIL'}")
