# Aluno: Tiago Bisolo Prestes

import sys

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

class CacheSimples:
    def __init__(self, kc, ram):
        self.ram = ram
        self.tam_cache = 2 ** kc
        self.dados = [0] * self.tam_cache
        self.bloco = -1
        self.modif = False

    def copiar_bloco_cache_para_ram(self, bloco_ender):
        endereco_inicio_bloco = bloco_ender * self.tam_cache
        endereco_fim_bloco = endereco_inicio_bloco + self.tam_cache

        acc = 0
        for i in range(endereco_inicio_bloco, endereco_fim_bloco):
            self.ram.write(i, self.dados[acc])
            acc += 1

    def atualizar_cache_com_novo_bloco(self, bloco_ender):
        endereco_inicio_bloco = bloco_ender * self.tam_cache
        endereco_fim_bloco = endereco_inicio_bloco + self.tam_cache

        acc = 0
        for i in range(endereco_inicio_bloco, endereco_fim_bloco):
            self.dados[acc] = self.ram.read(i)
            acc += 1

    def read(self, ender):
        bloco_ender = int(ender / self.tam_cache)

        if bloco_ender == self.bloco:
            print(f"Cache HIT(read): {ender}")
            pos = ender - self.bloco * self.tam_cache
            return self.dados[pos]
        else:
            print(f"Cache MISS(read): {ender}")
            if self.modif:
                self.copiar_bloco_cache_para_ram(bloco_ender)

            # Atualizar bloco RAM a ser lido
            self.atualizar_cache_com_novo_bloco(bloco_ender)

            pos = ender - bloco_ender * self.tam_cache
            self.modif = False # Reseta a flag de modificação
            self.bloco = bloco_ender # Atualiza com o número do novo bloco pego da memória RAM
            return self.dados[pos]

    def write(self, ender, val):
        bloco_ender = int(ender / self.tam_cache)

        if bloco_ender == self.bloco:
            print(f"cache HIT(write): {ender}")
            pos = ender - self.bloco * self.tam_cache
            self.dados[pos] = val # Escreve na memória cache o valor
        else:
            print(f"Cache MISS(write): {ender}")
            if self.modif:
                self.copiar_bloco_cache_para_ram(bloco_ender)

            self.atualizar_cache_com_novo_bloco(bloco_ender)

            pos = ender - bloco_ender * self.tam_cache
            self.dados[pos] = val # Escreve na memória cache o valor
            self.bloco = bloco_ender # Atualiza com o número do novo bloco pego da memória RAM

        self.modif = True

# Programa Principal

try:
    io = IO()
    ram = RAM(7)
    cache = CacheSimples(3, ram)  # tamanho da cache = 8
    cpu = CPU(cache, io)
    
    inicio = 10
    ram.write(inicio, 118)
    ram.write(inicio + 1, 130)
    cpu.run(inicio)
except EnderecoInvalido as e:
    print("Endereço inválido:", e.ender, file=sys.stderr)
