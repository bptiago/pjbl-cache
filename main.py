# Aluno: Tiago Bisolo Prestes

import sys
import math

class IO:
    def output(self, s):
        print(s, end='')

    def input(self, prompt):
        return input(prompt)


# Exceção (erro)
class EnderecoInvalido(Exception):
    def __init__(self, ender):
        self.ender = ender


class RAM:
    def __init__(self, k):
        self.tamanho = 2**k
        self.memoria = [0] * self.tamanho

    def verifica_endereco(self, ender):
        if (ender < 0) or (ender >= self.tamanho):
            raise EnderecoInvalido(ender)

    def capacidade(self):
        return self.tamanho

    def read(self, ender):
        self.verifica_endereco(ender)
        return self.memoria[ender]

    def write(self, ender, val):
        self.verifica_endereco(ender)
        self.memoria[ender] = val


class CPU:
    def __init__(self, mem, io):
        self.mem = mem
        self.io = io
        self.PC = 0                    # program counter
        self.A = self.B = self.C = 0   # registradores auxiliares

    def run(self, ender):
        self.PC = ender
        # lê "instrução" no endereço PC
        self.A = self.mem.read(self.PC)
        self.PC += 1
        self.B = self.mem.read(self.PC)
        self.PC += 1

        self.C = 1
        while self.A <= self.B:
            self.mem.write(self.A, self.C)
            self.io.output(f"{self.A} -> {self.C}\n")
            self.C += 1
            self.A += 1

class Cache:
    def __init__(self, tamanho_cache, tamanho_cache_line, ram):
        self.ram = ram
        self.tamanho_cache = 2 ** tamanho_cache
        self.tamanho_cache_line = 2 ** tamanho_cache_line # w
        self.num_cache_lines = int(self.tamanho_cache / self.tamanho_cache_line) # r
        self.cache_lines = [CacheLine(self.tamanho_cache_line) for _ in range(self.num_cache_lines)]

        self.num_bits_w = tamanho_cache_line
        self.num_bits_r = int(math.log(self.num_cache_lines, 2))

    def carregar_bloco_da_ram(self, s, r):
        cache_line = self.cache_lines[r]
        endereco_inicial_bloco = s * self.tamanho_cache_line
        for i in range(self.tamanho_cache_line):
            cache_line.dados[i] = self.ram.read(endereco_inicial_bloco + i)

    def copiar_bloco_para_ram(self, s, r):
        cache_line = self.cache_lines[r]
        endereco_inicial_bloco = s * self.tamanho_cache_line
        for i in range(self.tamanho_cache_line):
            self.ram.write(endereco_inicial_bloco + i, cache_line.dados[i])

    def read(self, endereco):
        # Descobrir r,w,t,s usando bitwise
        w = endereco & self.gerar_mascara_bit(self.num_bits_w) #
        r = (endereco >> self.num_bits_w) & self.gerar_mascara_bit(self.num_bits_r)
        t = (endereco >> self.num_bits_w + self.num_bits_r)
        s = endereco >> self.num_bits_w

        cache_line = self.cache_lines[r]

        if cache_line.tag == t:
            print(f"Cache hit (read): {endereco}")
        else:
            print(f"Cache miss (read): {endereco}")
            if cache_line.modificada:
                self.copiar_bloco_para_ram(s, r)

            self.carregar_bloco_da_ram(s, r)
            cache_line.tag = t
            cache_line.modificada = False

        return cache_line.dados[w]

    def write(self, endereco, valor):
        # Descobrir r,w,t,s usando bitwise
        w = endereco & self.gerar_mascara_bit(self.num_bits_w)  #
        r = (endereco >> self.num_bits_w) & self.gerar_mascara_bit(self.num_bits_r)
        t = (endereco >> self.num_bits_w + self.num_bits_r)
        s = endereco >> self.num_bits_w

        cache_line = self.cache_lines[r]

        if cache_line.tag == t:
            print(f"Cache hit (write): {endereco}")
        else:
            print(f"Cache miss (write): {endereco}")
            if cache_line.modificada:
                self.copiar_bloco_para_ram(s, r)

            self.carregar_bloco_da_ram(s, r)
            cache_line.tag = t
            cache_line.modificada = False

        cache_line.dados[w] = valor

        pass

    def gerar_mascara_bit(self, num_bits):
        return (1 << num_bits) - 1

class CacheLine:
    def __init__(self, tamanho_cache_line):
        self.tamanho_cache_line = tamanho_cache_line
        self.tag = None
        self.dados = [0] * self.tamanho_cache_line
        self.modificada = False

# Programa Principal

try:
    io = IO()
    ram = RAM(12)  # 4K de RAM (2**12)
    cache = Cache(7, 4, ram)  # total cache = 128 (2**7), cacheline = 16 palavras (2**4), numero cache lines = 8
    cpu = CPU(cache, io)
    inicio = 0
    ram.write(inicio, 110)
    ram.write(inicio + 1, 130)
    cpu.run(inicio)
except EnderecoInvalido as e:
    print("Endereço inválido:", e.ender, file=sys.stderr)
