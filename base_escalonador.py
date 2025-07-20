import random
import time
from collections import deque
from abc import ABC, abstractmethod
import math

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, tempo_chegada, possivelmente_catastrofico = False, prioridade=1, deadline=None):
        self.nome = nome            # Nome da tarefa (ex. Detecção de Obstáculo)
        self.duracao = duracao      # Tempo necessário para completar a tarefa (em segundos)
        self.prioridade = prioridade # Prioridade da tarefa (quanto menor o número, maior a prioridade)
        self.tempo_restante = duracao # Tempo restante para completar a tarefa
        self.tempo_inicio = None       # Hora em que a tarefa começa
        self.tempo_final = None        # Hora em que a tarefa termina
        self.tempo_chegada = tempo_chegada  # Tempo em que a tarefa chega
        self.tempo_em_espera = 0    # Tempo total de espera na fila
        self.tempo_de_resposta = None # Tempo desde a chegada até a primeira execução
        self.tempo_inicio_execucao_atual = None   # Hora em que a tarefa começa a execução no tempo atual
        self.tempo_final_execucao_atual = None    # Hora em que a tarefa termina a execução no tempo atual
        self.deadline = deadline
        self.possivelmente_catastrofico = possivelmente_catastrofico # Define se a não-realização da tarefa é possivelmente catastrófica
        self.tempos_execucao = [] # Lista de tuplas (inicio, fim) de cada burst de execução

    def __str__(self):
        return f"Tarefa {self.nome} (Prioridade {self.prioridade}): {self.duracao} segundos"

    def executar(self, quantum):
        """Executa a tarefa por um tempo de 'quantum' ou até terminar"""
        tempo_exec = min(self.tempo_restante, quantum)
        self.tempo_restante -= tempo_exec
        return tempo_exec

# Cada processo tem um nome, um tempo total de execução (tempo_execucao),
# e um tempo restante (tempo_restante), que é decrementado conforme o processo vai sendo executado.
# O método executar(quantum) executa o processo por uma quantidade limitada de tempo (quantum) ou até ele terminar.

# Classe abstrata de Escalonador
class EscalonadorCAV(ABC):
    def __init__(self):
        self.tarefas: list[TarefaCAV] = []
        self.menor_tarefa = None
        self.sobrecarga_total = 0  # Sobrecarga total acumulada
        self.tempo_atual = 0

    def adicionar_tarefa(self, tarefa: TarefaCAV):
        """Adiciona uma tarefa (ação do CAV) à lista de tarefas"""
        self.tarefas.append(tarefa)
        if (self.menor_tarefa is None):
            self.menor_tarefa = tarefa
        else:
            if (tarefa.duracao < self.menor_tarefa.duracao):
                self.menor_tarefa = tarefa

    @abstractmethod
    def escalonar(self):
        """Método que será implementado pelos alunos para o algoritmo de escalonamento"""
        pass

    def registrar_sobrecarga(self, tempo):
        """Adiciona tempo de sobrecarga ao total"""
        self.sobrecarga_total += tempo

    def exibir_sobrecarga(self):
        """Exibe a sobrecarga total acumulada"""
        print(f"Sobrecarga total acumulada: {self.sobrecarga_total} segundos.\n")
        
    def calcular_e_exibir_metricas(self, tarefas):
        """
        Calcula e exibe o tempo de turnaround médio e a sobrecarga total
        para a simulação.
        """
        tempos_de_turnaround = []
        if not tarefas:
            print("Nenhuma tarefa para calcular métricas.")
            return

        print("\n--- Resultados da Simulação ---")
        for tarefa in tarefas:
            if tarefa.tempo_final != None:  # Calcula apenas para tarefas que foram concluídas
                turnaround = tarefa.tempo_final - tarefa.tempo_chegada
                tempos_de_turnaround.append(turnaround)
                print(f"  - Tarefa '{tarefa.nome}':")
                print(
                    f"    - Chegada: {tarefa.tempo_chegada:.2f}s, Conclusão: {tarefa.tempo_final:.2f}s")
                print(f"    - Tempo de Turnaround: {turnaround:.2f}s")
            else:
                print(f"  - Tarefa '{tarefa.nome}' não foi concluída.")

        if tempos_de_turnaround:
            avg_turnaround = sum(tempos_de_turnaround) / \
                len(tempos_de_turnaround)
            print(f"**Turnaround Médio**: {avg_turnaround:.2f} segundos.")
        else:
            print("**Turnaround Médio**: N/A (Nenhuma tarefa concluída).")

        print(
            f"**Sobrecarga Total Acumulada**: {self.sobrecarga_total:.2f} segundos.")
        print("------------------------------\n")

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).

class EscalonadorFIFO(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento FIFO para veículos autônomos"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada  # Inicializa o relógio da simulação
            for tarefa in self.tarefas:
                tarefa.tempo_inicio = max(self.tempo_atual, tarefa.tempo_chegada)
                tarefa.tempo_inicio_execucao_atual = tarefa.tempo_inicio
                
                self.tempo_atual = tarefa.tempo_inicio
                print(
                    f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos. (chegada: {tarefa.tempo_chegada}s)")
                time.sleep(tarefa.duracao / 10)  # Simula a execução da tarefa 10x mais rápido
                self.tempo_atual += tarefa.duracao
                
                tarefa.tempo_final_execucao_atual = self.tempo_atual
                tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                tarefa.tempo_final = self.tempo_atual
                tarefa.tempo_em_espera = tarefa.tempo_inicio - tarefa.tempo_chegada
                tarefa.tempo_de_resposta = tarefa.tempo_em_espera
                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                #self.registrar_sobrecarga(0.5)  # 0.5 segundos de sobrecarga por tarefa (simulando troca de contexto)
                print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}")

        self.exibir_sobrecarga()

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.

class EscalonadorSJF(EscalonadorCAV):

    def escalonar(self):
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)

        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada

            while fila: 
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.duracao)
                if len(tarefas_que_chegaram) > 0: 
                    tarefa = tarefas_que_chegaram[0]
                    fila.remove(tarefa)

                tarefa.tempo_inicio = max(self.tempo_atual, tarefa.tempo_chegada)
                tarefa.tempo_inicio_execucao_atual = tarefa.tempo_inicio
                
                self.tempo_atual = tarefa.tempo_inicio
                print(
                    f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos. (chegada: {tarefa.tempo_chegada}s e deadline: {tarefa.deadline})")
                time.sleep(tarefa.duracao / 10)  # Simula a execução da tarefa 10x mais rápido
                self.tempo_atual += tarefa.duracao
                
                tarefa.tempo_final_execucao_atual = self.tempo_atual
                tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                tarefa.tempo_final = self.tempo_atual
                tarefa.tempo_em_espera = tarefa.tempo_inicio - tarefa.tempo_chegada
                tarefa.tempo_de_resposta = tarefa.tempo_em_espera
                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                #self.registrar_sobrecarga(0.5)  # 0.5 segundos de sobrecarga por tarefa (simulando troca de contexto)
                print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}")

        self.exibir_sobrecarga()

class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefa = tarefas_que_chegaram[0]
                fila.remove(tarefa)
                if tarefa.tempo_restante > 0:
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - (tarefa.tempo_final_execucao_atual if tarefa.tempo_final_execucao_atual is not None else 0)
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s)")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")

        self.exibir_sobrecarga()

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.

class EscalonadorEDF(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.deadline)

                if len(tarefas_que_chegaram) > 0: 
                    tarefa = tarefas_que_chegaram[0]
                    fila.remove(tarefa)

                if tarefa.tempo_restante > 0:
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - (tarefa.tempo_final_execucao_atual if tarefa.tempo_final_execucao_atual is not None else 0)
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s) e deadline: {tarefa.deadline}")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")

        self.exibir_sobrecarga()

class EscalonadorPrioridadeNP(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento por Prioridade (menor número = maior prioridade)"""
        print("Escalonamento por Prioridade:")
        # Ordena as tarefas pela prioridade
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)

        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            while (fila):
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual += 1
                    continue
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.prioridade)
                
                tarefa = tarefas_que_chegaram[0]
                fila.remove(tarefa)
                
                # Executando a tarefa
                tarefa.tempo_inicio = self.tempo_atual
                tarefa.tempo_inicio_execucao_atual = tarefa.tempo_inicio
                
                print(f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos com prioridade {tarefa.prioridade}. (chegada: {tarefa.tempo_chegada}s)")
                time.sleep(tarefa.duracao / 10)
                
                self.tempo_atual += tarefa.duracao
                tarefa.tempo_final = self.tempo_atual
                tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                tarefa.tempo_em_espera = tarefa.tempo_de_resposta
                tarefa.tempo_final_execucao_atual = self.tempo_atual
                tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))

                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                # self.registrar_sobrecarga(0.4)  # 0.4 segundos de sobrecarga por tarefa
                print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")

        self.exibir_sobrecarga()

class EscalonadorPrioridadeP(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento por prioridade preemptivo com tarefas de CAVs"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefas_que_chegaram.sort(key=lambda tarefas: tarefas.prioridade)

                if len(tarefas_que_chegaram) > 0: 
                    tarefa = tarefas_que_chegaram[len(tarefas_que_chegaram)-1]
                    fila.remove(tarefa)

                if tarefa.tempo_restante > 0:
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - (tarefa.tempo_final_execucao_atual if tarefa.tempo_final_execucao_atual is not None else 0)
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s e prioridade: {tarefa.prioridade})")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")

        self.exibir_sobrecarga()

class EscalonadorUG(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum
        self.quantum_atual = quantum

    def urgencia(self, prioridade, deadline, tempo_resta, urg_max):
        if deadline > tempo_resta: return prioridade/(deadline-tempo_resta)
        return urg_max + 1
    
    #urg_max é urgencia máxima, que vai servir de parâmetro de comparação para decidir se o quantum aumenta ou não
    def escalonar(self, urg_max=1/2):
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
    
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.prioridade)
                tarefa = tarefas_que_chegaram[len(tarefas_que_chegaram)-1]
                fila.remove(tarefa)

                if tarefa.tempo_restante > 0:
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    urgencia = self.urgencia(tarefa.prioridade, tarefa.deadline, tarefa.tempo_restante, urg_max)
                    if urgencia > urg_max:
                        self.quantum_atual += 1
                        tempo_exec = min(tarefa.tempo_restante, self.quantum_atual)
                    else:
                        tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - (tarefa.tempo_final_execucao_atual if tarefa.tempo_final_execucao_atual is not None else 0)
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s, urgencia: {urgencia} e deadline: {tarefa.deadline})")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")
                        if urgencia > urg_max: self.quantum_atual = self.quantum

        self.exibir_sobrecarga()

class EscalonadorFutureVision(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def limite(self, tarefas_que_chegaram):
        if (len(tarefas_que_chegaram) > 0):
            duracao_total = 0
            menor_chegada = tarefas_que_chegaram[0].tempo_chegada 
            maior_chegada = tarefas_que_chegaram[0].tempo_chegada

            for tarefa in tarefas_que_chegaram: 
                duracao_total += tarefa.tempo_restante
                menor_chegada = min(menor_chegada, tarefa.tempo_chegada)
                maior_chegada = max(maior_chegada, tarefa.tempo_chegada)

            duracao_media = duracao_total/len(tarefas_que_chegaram)
            intervalo = (maior_chegada + menor_chegada)//2
            lim_espera = duracao_media + intervalo
            return lim_espera
        return 0

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.tempo_restante)
                tarefa = tarefas_que_chegaram[0]
                tarefa_maior_que_limite = None
                
                
                
                for t in tarefas_que_chegaram:
                    tempo_aguardando = self.tempo_atual - t.tempo_final_execucao_atual if (
                        t.tempo_final_execucao_atual is not None) else self.tempo_atual - t.tempo_chegada
                    if tempo_aguardando > self.limite(tarefas_que_chegaram):
                        tarefa_maior_que_limite = t
                        break
                if tarefa_maior_que_limite is not None:
                    tarefa = tarefa_maior_que_limite
                    
                fila.remove(tarefa)

                if tarefa.tempo_restante > 0:
                    tempo_aguardando = self.tempo_atual - tarefa.tempo_final_execucao_atual if (
                        tarefa.tempo_final_execucao_atual is not None) else (tarefa.tempo_de_resposta if tarefa.tempo_de_resposta is not None else self.tempo_atual - tarefa.tempo_chegada)
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - (tarefa.tempo_final_execucao_atual if tarefa.tempo_final_execucao_atual is not None else 0)
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s, limite de espera: {self.limite(tarefas_que_chegaram)}s, tempo_espera: { (tempo_aguardando)}s)")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempos_execucao.append((tarefa.tempo_inicio_execucao_atual, tarefa.tempo_final_execucao_atual))
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\nBursts: {tarefa.tempos_execucao}\n")

        self.exibir_sobrecarga()

class CAV:
    def __init__(self, id):
        self.id = id  # Identificador único para cada CAV
        self.tarefas = []  # Lista de tarefas atribuídas a esse CAV 

    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)

    def executar_tarefas(self, escalonador):
        print(f"CAV {self.id} começando a execução de tarefas...\n")
        escalonador.escalonar()
        print(f"CAV {self.id} terminou todas as suas tarefas.\n")

# Função para criar algumas tarefas fictícias
def criar_tarefas():
    tarefas = [
        TarefaCAV("Detecção de Obstáculo", 10, prioridade=100, tempo_chegada=5, possivelmente_catastrofico=True, deadline=16),
        TarefaCAV("Planejamento de Rota", 5, prioridade=2, tempo_chegada=5, possivelmente_catastrofico=False, deadline=3),
        TarefaCAV("Manutenção de Velocidade", 3, prioridade=3, tempo_chegada=30, possivelmente_catastrofico=False, deadline=1),
        TarefaCAV("Comunicando com Infraestrutura", 20, prioridade=1, tempo_chegada=1, possivelmente_catastrofico=False, deadline=20),
        TarefaCAV("Aumento de Velocidade", 15, prioridade=3, tempo_chegada=6, possivelmente_catastrofico=False, deadline=13),
        TarefaCAV("Aumentar volume do rádio", 8, prioridade=5, tempo_chegada=2, possivelmente_catastrofico=False, deadline=55),
        #TarefaCAV("Comunicação de SOS", random.randint(10, 15), prioridade=1, tempo_chegada=22, possivelmente_catastrofico=True, deadline=90),
        #TarefaCAV("Reconhecimento de Sinais de Trânsito", random.randint(3, 6), prioridade=2, tempo_chegada=8, possivelmente_catastrofico=False, deadline=8),
        #TarefaCAV("Monitoramento de Ponto Cego", random.randint(4, 8), prioridade=2, tempo_chegada=12, possivelmente_catastrofico=True, deadline=27),
        #TarefaCAV("Análise de Condições Climáticas", random.randint(2, 5), prioridade=3, tempo_chegada=15, possivelmente_catastrofico=False, deadline=666),
        #TarefaCAV("Atualização de Mapas", random.randint(5, 9), prioridade=4, tempo_chegada=50, possivelmente_catastrofico=False, deadline=157),
        #TarefaCAV("Detecção de Faixa de Rodagem", random.randint(3, 6), prioridade=2, tempo_chegada=9, possivelmente_catastrofico=False),
        #TarefaCAV("Verificação de Sistemas Internos", random.randint(2, 4), prioridade=4, tempo_chegada=25, possivelmente_catastrofico=False),
        #TarefaCAV("Ajuste de Suspensão", random.randint(2, 3), prioridade=5, tempo_chegada=35, possivelmente_catastrofico=False),
        #TarefaCAV("Resfriamento de Bateria", random.randint(3, 6), prioridade=3, tempo_chegada=20, possivelmente_catastrofico=False, deadline=0),
        #TarefaCAV("Manobra de Ultrapassagem", random.randint(6, 10), prioridade=1, tempo_chegada=11, possivelmente_catastrofico=True),
        #TarefaCAV("Redução de Velocidade", random.randint(2, 4), prioridade=2, tempo_chegada=3, possivelmente_catastrofico=False),
        #TarefaCAV("Recarregamento por Indução", random.randint(5, 7), prioridade=4, tempo_chegada=90, possivelmente_catastrofico=False, deadline=22),
        #TarefaCAV("Monitoramento de Passageiros", random.randint(1, 2), prioridade=5, tempo_chegada=6, possivelmente_catastrofico=False),
        #TarefaCAV("Envio de Diagnóstico Remoto", random.randint(3, 6), prioridade=4, tempo_chegada=27, possivelmente_catastrofico=False),
    ]
    return tarefas

# Exemplo de uso
if __name__ == "__main__":
    # Criar algumas tarefas fictícias
    tarefas = criar_tarefas()

    # Criar um CAV
    cav = CAV(id=1)
    for t in tarefas:
        cav.adicionar_tarefa(t)


    print("Simulando CAV com Prioridade P:\n")
    escalonador_p = EscalonadorPrioridadeP(2)
    for t in tarefas:
        escalonador_p.adicionar_tarefa(t)

    simulador_p = CAV(id=1)
    simulador_p.executar_tarefas(escalonador_p)
    escalonador_p.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    print("Simulando CAV com EDF:\n")
    escalonador_EDF = EscalonadorEDF(2)
    for t in tarefas:
        escalonador_EDF.adicionar_tarefa(t)

    simulador_EDF = CAV(id=1)
    simulador_EDF.executar_tarefas(escalonador_EDF)
    escalonador_EDF.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    print("Simulando CAV com SJF:\n")
    escalonador_SJF = EscalonadorSJF()
    for t in tarefas:
        escalonador_SJF.adicionar_tarefa(t)

    simulador_SJF = CAV(id=1)
    simulador_SJF.executar_tarefas(escalonador_SJF)
    escalonador_SJF.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    # Criar um escalonador FIFO
    print("Simulando CAV com FIFO:\n")
    escalonador_fifo = EscalonadorFIFO()
    for t in tarefas:
        escalonador_fifo.adicionar_tarefa(t)
        
    simulador_fifo = CAV(id=1)
    simulador_fifo.executar_tarefas(escalonador_fifo)
    escalonador_fifo.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3)
    for t in tarefas:
        escalonador_rr.adicionar_tarefa(t)

    simulador_rr = CAV(id=1)
    simulador_rr.executar_tarefas(escalonador_rr)
    escalonador_rr.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridadeNP()
    for t in tarefas:
        escalonador_prio.adicionar_tarefa(t)

    simulador_prio = CAV(id=1)
    simulador_prio.executar_tarefas(escalonador_prio)
    escalonador_prio.calcular_e_exibir_metricas(tarefas)

    tarefas = criar_tarefas()

    # Criar um escalonador por Último gás
    print("\nSimulando CAV com Escalonamento por Último Gás:\n")
    escalonador_ug = EscalonadorUG(3)
    for t in tarefas:
        escalonador_ug.adicionar_tarefa(t)

    simulador_ug = CAV(id=1)
    simulador_ug.executar_tarefas(escalonador_ug)
    escalonador_ug.calcular_e_exibir_metricas(tarefas)
    
    tarefas = criar_tarefas()
    
    print("\nSimulando CAV com Escalonamento por visão do futuro:\n")
    escalonador_vf = EscalonadorFutureVision(3)
    for t in tarefas:
        escalonador_vf.adicionar_tarefa(t)

    simulador_vf = CAV(id=1)
    simulador_vf.executar_tarefas(escalonador_vf)
    escalonador_vf.calcular_e_exibir_metricas(tarefas)
