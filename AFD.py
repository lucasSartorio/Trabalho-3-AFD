import graphviz
from collections import deque, defaultdict

class Automato:
    def __init__(self, estados, alfabeto, transicoes, q0, finais):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transicoes = transicoes
        self.q0 = q0
        self.finais = finais

    def simular_afn(self, cadeia):
        """
        Simula o processamento de uma cadeia no AFN.
        """
        estados_atuais = {self.q0}
        
        print(f"\n--- Simulando cadeia: '{cadeia}' ---")
        print(f"Estado inicial: {estados_atuais}")

        for simbolo in cadeia:
            proximos_estados = set()
            if simbolo not in self.alfabeto:
                print(f"Erro: Símbolo '{simbolo}' não pertence ao alfabeto.")
                return False
            
            for estado in estados_atuais:
                if (estado, simbolo) in self.transicoes:
                    destinos = self.transicoes[(estado, simbolo)]
                    proximos_estados.update(destinos)
            
            estados_atuais = proximos_estados
            print(f"Lendo '{simbolo}' -> Novos estados: {estados_atuais}")
            
            if not estados_atuais:
                break


        aceita = any(estado in self.finais for estado in estados_atuais)
        return aceita

    def desenhar(self, nome_arquivo="automato"):
        """
        Gera um arquivo de imagem (PDF/PNG) do autômato usando Graphviz.
        """
        dot = graphviz.Digraph(comment='Autômato')
        dot.attr(rankdir='LR') 

        # Nós
        for estado in self.estados:
            if estado in self.finais:
                dot.node(estado, shape='doublecircle')
            else:
                dot.node(estado, shape='circle')
        
        dot.node('start', shape='point')
        dot.edge('start', self.q0)

        arestas = defaultdict(list)
        for (origem, simbolo), destinos in self.transicoes.items():
            for destino in destinos:
                arestas[(origem, destino)].append(simbolo)
        
        for (origem, destino), simbolos in arestas.items():
            label = ",".join(sorted(simbolos))
            dot.edge(origem, destino, label=label)

        try:
            caminho = dot.render(nome_arquivo, format='png', cleanup=True)
            print(f"Diagrama salvo como: {caminho}")
        except Exception as e:
            print(f"Aviso: Não foi possível gerar o gráfico visual. Verifique se o Graphviz está instalado no sistema. Erro: {e}")

def converter_afn_para_afd(afn):
    """
    Converte um AFN para AFD usando o Algoritmo de Construção de Subconjuntos.
    """
    
    q0_afd = frozenset([afn.q0])
    
    estados_processados = set()
    fila = deque([q0_afd])
    
    transicoes_afd = {}
    todos_estados_afd = set([q0_afd])
    
    while fila:
        estados_atuais = fila.popleft()
        estados_processados.add(estados_atuais)
        
        for simbolo in afn.alfabeto:
            novos_estados = set()
            for sub_estado in estados_atuais:
                if (sub_estado, simbolo) in afn.transicoes:
                    novos_estados.update(afn.transicoes[(sub_estado, simbolo)])
            
            if novos_estados:
                novo_estado_frozenset = frozenset(novos_estados)
                transicoes_afd[(estados_atuais, simbolo)] = set([novo_estado_frozenset])
                
                if novo_estado_frozenset not in todos_estados_afd:
                    todos_estados_afd.add(novo_estado_frozenset)
                    fila.append(novo_estado_frozenset)

    mapa_nomes = {}
    for est_set in todos_estados_afd:
        nome_limpo = "{" + ",".join(sorted(list(est_set))) + "}"
        mapa_nomes[est_set] = nome_limpo

    Q_afd = list(mapa_nomes.values())
    F_afd = []
    for est_set, nome in mapa_nomes.items():
        if any(sub in afn.finais for sub in est_set):
            F_afd.append(nome)

    delta_afd = {}
    for (origem, simbolo), destinos in transicoes_afd.items():
        destino = list(destinos)[0]
        nome_origem = mapa_nomes[origem]
        nome_destino = mapa_nomes[destino]
        delta_afd[(nome_origem, simbolo)] = {nome_destino}

    return Automato(
        estados=Q_afd,
        alfabeto=afn.alfabeto,
        transicoes=delta_afd,
        q0=mapa_nomes[q0_afd],
        finais=F_afd
    )

def ler_entrada_usuario():
    print("=== Definição do AFN ===")
    print("Digite os estados separados por vírgula (ex: q0,q1):")
    Q = input().strip().split(',')
    Q = [q.strip() for q in Q]

    print("Digite o alfabeto separado por vírgula (ex: 0,1):")
    Sigma = input().strip().split(',')
    Sigma = [s.strip() for s in Sigma]

    print("Digite o estado inicial (ex: q0):")
    q0 = input().strip()

    print("Digite os estados finais separados por vírgula (ex: q1):")
    F = input().strip().split(',')
    F = [f.strip() for f in F]

    print("Digite as transições. Digite 'FIM' para parar.")
    print("Formato: q0,0 -> q0,q1  (Use vírgula para múltiplos destinos)")
    
    delta = {}
    
    while True:
        linha = input("> ").strip()
        if linha.upper() == 'FIM':
            break
        if '->' not in linha:
            continue
            
        try:
            parte_esq, parte_dir = linha.split('->')
            origem, simbolo = parte_esq.split(',')
            origem = origem.strip()
            simbolo = simbolo.strip()
            
            destinos = parte_dir.split(',')
            destinos = {d.strip() for d in destinos}
            
            if (origem, simbolo) in delta:
                delta[(origem, simbolo)].update(destinos)
            else:
                delta[(origem, simbolo)] = destinos
        except:
            print("Erro de formato. Tente: estado,simbolo -> destino1,destino2")

    return Automato(Q, Sigma, delta, q0, F)

if __name__ == "__main__":
    afn = ler_entrada_usuario()
    
    print("\nGerando diagrama do AFN...")
    afn.desenhar("AFN_Diagrama")

    while True:
        print("\nDigite uma cadeia para testar (ou 'SAIR' para converter para AFD):")
        cadeia = input("Cadeia: ").strip()
        if cadeia.upper() == 'SAIR':
            break
        
        resultado = afn.simular_afn(cadeia)
        print(f"Resultado: {'ACEITA' if resultado else 'REJEITA'}")

    print("\n=== Convertendo para AFD equivalente ===")
    afd = converter_afn_para_afd(afn)
    
    print("Quíntupla do AFD:")
    print(f"Q' = {afd.estados}")
    print(f"Σ  = {afd.alfabeto}")
    print(f"q0'= {afd.q0}")
    print(f"F' = {afd.finais}")
    print("δ' (Transições):")
    for (origem, simbolo), destino in afd.transicoes.items():
        print(f"  ({origem}, {simbolo}) -> {list(destino)[0]}")

    print("\nGerando diagrama do AFD...")
    afd.desenhar("AFD_Equivalente")
    print("\nPrograma finalizado.")