class Stack:
  #construtor
  def __init__(self):
    self.stack = list()
  def top(self):
    if len(self.stack) > 0:
      return self.stack[len(self.stack)-1]
  def subtop(self):
    if len(self.stack) > 1:
      return self.stack[len(self.stack) - 2]
  #push stack
  def push_stack(self, value = '$', type = '$', scope = '$'):
      self.stack.append({'value':value, 'type': type, 'scope': scope})
  #pop 
  def pop_stack(self):
    if len(self.stack) > 0:
      self.stack.pop()
  #search by value
  def search(self, value):
    if len(self.stack) > 0:
      for l in reversed(self.stack):
        if value == l['value']:
          return l['type'], True
      return "null", False
    else:
      print("Empty stack")

  #search, but only for declaration
  def search_var(self, value, scope):
    if len(self.stack) > 0:
      for l in reversed(self.stack):
        if value == l['value'] and scope == l['scope']:
          return True
      return False
    else:
      print("Empty stack")


class Token:
  def __init__(self, token, tipo, linha) -> None:
    self.token = token
    self.tipo = tipo
    self.linha = linha

class Sintatico:
  def __init__(self, listTokens):
    self.tokens = listTokens
    self.posicao = 0
    self.erros = list()
    self.token = tokens[0]
    self.pilha = Stack()
    self.scope = 0 #Scope -> não é necessário se usar o marcador
    self.x = 0 #Controle de entrada e saída de begin
    self.pct = list() #Pilha para tipos
  #Avança token
  def next(self):
    if(self.posicao + 1 < len(self.tokens)):
      self.posicao += 1
      self.token = tokens[self.posicao]

  #program inicia e terminará a análise
  def program(self):
    if self.token.token == "program":
      #Primeiro elemento de pilha
      self.pilha.push_stack("$")
      self.next()  
      if self.token.tipo == "id":
        self.pilha.push_stack(self.token.token, "program", self.scope)
        self.next()
        if self.token.token == ";":
          self.next()
          self.declaracao_variaveis()
          self.declaracao_de_subprogramas()
          self.comando_composto()
          if self.token.tipo == "nls":
            self.erros.append(f"'{self.token.token}' unrecognized language symbol, line {self.token.linha}\nCompilation aborted!")
          elif self.token.token != ".":
            self.erros.append(". expected at the end of the program")
        else:
          self.erros.append(f"[{self.token.linha}] ; missing")
      else:
        self.erros.append(f"[{self.token.linha}] ID inválido")
    else:
      self.erros.append(f"[{self.token.linha}] Inicializador program não encontrado")     

  #bloco de declaração de variáveis
  def declaracao_variaveis(self):
    if(self.token.token == "var"): #esse if impede e volta pra program
      self.next()
      self.lista_declaracao_variaveis()
    #token ->  ε
    else:
      pass
    
  def lista_declaracao_variaveis(self):
    self.lista_indentificadores()
    if self.token.token == ":":
      self.next()
      self.tipo()
      if self.token.token != ";":
        self.erros.append(f"; missing, line {self.tokens[self.posicao - 1].linha}")
      else:
        self.next()

      if self.token.tipo == "id":
        self.lista_declaracao_variaveis()
    elif self.token.tipo != "nls":
      self.erros.append(f"[{self.token.linha}] : expected")
    
  def lista_indentificadores(self):
    if self.token.tipo in ["id", "keyword"]:
      #escopo inicial
      self.pilha.push_stack("var_marker")
      #verifica se já foi declarado, se for, então há erro de redeclaração  
      if not self.pilha.search_var(self.token.token, self.scope):
        self.pilha.push_stack(self.token.token, "unknown", self.scope)
      #não foi declarado
      else:
        self.erros.append(f"'{self.token.token}' has already been declared, line {self.token.linha}")

      if self.token.tipo == "keyword":
        self.erros.append(f"{self.token.token} is a keyword, line {self.token.linha}")
      self.next()
      self.lista_indentificadores2()

    elif self.token.tipo != "nls":
      self.erros.append(f"[{self.token.linha}] id inválido {self.token.token}")

  def lista_indentificadores2(self): #,id(ldi')/ ε
    if self.token.token == ",":
      self.next()
      
      #para semântico, se esperar outro(s) id(s)
      if not self.pilha.search_var(self.token.token, self.scope):
        self.pilha.push_stack(self.token.token, "unknown", self.scope)
      #não foi declarado
      else:
        self.erros.append(f"'{self.token.token}' has already been declared, line {self.token.linha}")
      
      #se espera um id
      if self.token.tipo in ["id", "keyword"]:
        if self.token.tipo == "keyword":
          self.erros.append(f"{self.token.token} is a keyword, line {self.token.linha}")
        self.next()
        self.lista_indentificadores2()
      elif self.token.tipo != "nls":
        self.erros.append(f"ID inválido {self.token.token}")

    else:
      pass
  
  def tipo(self):
    if(self.token.token in ['real','integer','boolean']):
      self.atribuirTipo()

      self.next()
    elif self.token.tipo != "nls":
      self.erros.append(f"{self.token.token}: Tipo inválido")
      self.next()

  def declaracao_de_subprogramas(self): #D_SUBPROGMS
    if self.token.token == "procedure":
      self.next()
      self.declaracao_de_subprograma()
      if self.token.token == ";":
        self.next()
      else:
        self.erros.append("procedure: Expected ';' after end")

      self.declaracao_de_subprogramas()

  def declaracao_de_subprograma(self): #d_subprgm
    if self.token.tipo == "id":
      #se não foi declarado nada igual no mesmo escopo
      if not self.pilha.search_var(self.token.token, self.scope):
        self.pilha.push_stack(self.token.token, "procedure", self.scope)
      #já foi declarado algo com esse id no mesmo escopo
      else:
        self.erros.append(f"{self.token.token} have already been declared")
      self.pilha.push_stack("$")
      self.scope += 1
      self.next()
    else:
      self.erros.append(f"ID inválido, {self.token.token}")
    
    self.argumentos()
    
    if self.token.token == ";":
      self.next()
    else:
      self.erros.append(f"; missing, line {self.tokens[self.posicao].linha}")


    self.declaracao_variaveis()
    self.declaracao_de_subprogramas()
    self.comando_composto()
    
  def argumentos(self):
    if self.token.token == "(":
      self.next()

      if self.token.token in ");":
        if self.token.token == ";":
          self.erros.append(f") expected, line {self.token.linha}")
        else:
          self.next()
      else:
        self.lista_de_parametros()
        if self.token.token == ")":
          self.next()
        elif self.token.tipo != "nls":
          self.erros.append(") expected")

    else:
      pass

  def lista_de_parametros(self):
    self.lista_indentificadores()
    if(self.token.token == ":" or self.token.token == ";"):
      if self.token.token == ";":
          self.erros.append("; is not :")
      self.next()  
    elif self.token.tipo != "nls":
      self.erros.append(": expected")
    
    self.tipo()
    self.lista_de_parametros2()
  
  def lista_de_parametros2(self):
    if self.token.token in ";,":
      if self.token.token == ",":
        self.erros.append(f"', is not ;', line {self.token.linha}")

      self.next()
      self.lista_indentificadores()

      if(self.token.token == ":"):
        self.next()
        
      elif self.token.tipo != "nls":
        self.erros.append(": expected")  

      self.tipo()

      self.lista_indentificadores2()

    else:
      pass

  def comando_composto(self):
    if self.token.token == "begin":
      self.x += 1
      self.next()
      self.comandos_opcionais()
      if self.token.token == "end":
        self.next()
      elif self.token.tipo != "nls":
        self.erros.append(f"Expected end, line {self.token.linha}")
      #garantindo o fim do escopo, iremos limpá-lo da pilha
      self.x -= 1
      if self.x == 0:
        self.cleanScope()
    
    elif self.token.tipo != "nls":
      self.erros.append(f"begin expected {self.token.linha}, but started with {self.token.token}")

  def comandos_opcionais(self):
    self.lista_de_comandos()
  
  def lista_de_comandos(self):
    self.comando()
    self.lista_de_comandos2()


  def lista_de_comandos2(self):
    if self.token.token == ";":
      self.next()
    if self.token.token in ['begin','(','if','while','for'] or self.token.tipo == "id":
      token_anterior = self.tokens[self.posicao-1]
      if token_anterior.token != ";":
        self.erros.append(f"; missing, line {token_anterior.linha}")
      self.comando()
      self.lista_de_comandos2()
  

  def comando(self):
    #se lê ID
    if self.token.tipo == "id":
      tipo, declared = self.pilha.search(self.token.token)
      #Não achou na pilha de declaração
      if not declared:
        self.erros.append(f"{self.token.token} was not declared, line {self.token.linha}")
      #Achou, mas é identificador de programa
      elif tipo == "program":
        self.erros.append(f"{self.token.token} is program identifier")
        self.pct.append("erro")
      #ID declarado, vai pra tipo
      else:
        if tipo in ["real", "integer", "boolean"]:
          self.pct.append(tipo)
      
      self.next()
      #adiciona erro pois procedure recebe :=
      if self.token.token in ":=" and tipo == "procedure":
        self.erros.append(f"{self.tokens[self.posicao-1].token} is a procedure, line {self.token.linha}")
        while self.token.token != ";":
          self.next()
          self.erros.append(f"[{self.token.token}] invalid assignment to procedure , line {self.tokens[self.posicao - 1].linha}")
        self.next()
      #atribuição a variável (não-procedure)
      elif self.token.token in ":=":
        linha = self.token.linha
        
        if self.token.token != ":=":
          self.erros.append(f"'{self.token.token}' line {self.token.linha}, use :=")
        
        self.next() 
        self.expressao()

        if not self.verifySubTop():
          self.erros.append(f"Invalid assignment '{self.pct[len(self.pct)-1]}' -> {self.pct[len(self.pct)-2]}, line {linha}")
        self.clean_stack()
      
      elif self.token.token == "(":
        if tipo != "procedure":
          self.erros.append(f"{self.tokens[self.posicao-1].token} is not a procedure, line {self.token.linha}")
        self.ativacao_de_procedimento()
        
        #procedimento com atribuição -> erro 
        while self.token.token != ";":
          self.next()
          self.erros.append(f"[{self.token.token}] invalid assignment to procedure , line {self.tokens[self.posicao - 1].linha}")
          
      elif self.token.tipo != "nls" and self.token.token != ";":
        self.erros.append(f"assignment error or procedure call after {self.tokens[self.posicao-1].token}, line {self.tokens[self.posicao-1].linha}")
        if(self.tokens[self.posicao+1].token == ";"):
          self.next()
    
      
    elif self.token.token == "if":
      linha = self.token.linha
      self.next()

      self.expressao()

      #saída deve ser operador boolean
      if not self.verificaRel():
        self.erros.append(f"Invalid expression for if, line {linha}")
      
      self.clean_stack()
      if self.token.token == "then":
        self.next()
      elif self.token.tipo != "nls":
        self.erros.append("expected [then keyword]")

      self.comando() 
      if self.token.token == ";":
        self.next()
      self.parte_else()

    elif self.token.token == "while":
      linha = self.token.linha
      
      self.next()
      #while()
      self.expressao()
      
      #saída deve ser operador boolean
      if not self.verificaRel():
        self.erros.append(f"Invalid expression for while, line {linha}")
      self.clean_stack()

      if self.token.token == "do":
        self.next()
      elif self.token.tipo != "nls":
        self.erros.append(f"Expected 'do' keyword, line {linha}")
      
      self.comando()

      if self.token.token == ";":
        self.next()

    #begin end
    elif self.token.token == "begin":
      self.comando_composto()


    #for
    elif self.token.token == "for":
      self.next()
      #mesmo se estiver errado (keyword) ele entra, pois pode ter escrito errado
      if self.token.tipo in ["id","keyword"]:
        tipo, declared = self.pilha.search(self.token.token)
        #Não achou na pilha de declaração
        if not declared:
          self.erros.append(f"{self.token.token} was not declared, line {self.token.linha}")
        #Achou, mas é identificador de programa
        elif tipo == "program":
          self.erros.append(f"{self.token.token} is program identifier")
        #ID declarado, vai pra tipo
        elif tipo == "real":
          self.erros.append(f"[for] id expect integer")
        else:
            self.pct.append(tipo)

        if self.token.tipo == "keyword":
          self.erros.append(f"{self.token.token} is a keyword")
        self.next()
      
      #se não for id, keyword ou um símbolo não pertencente a linguagem
      elif self.token.tipo != "nls":
        self.erros.append("Identifier expected")
      
      #espera-se :=
      if self.token.token in ":=":
        if self.token.token != ":=":
          self.erros.append(f"'{self.token.token}' line {self.token.linha}, use :=")
        self.next()

      elif self.token.tipo != "nls":
        self.erros.append(f":= expected, line {self.token.linha}")

      #espera-se number integer
      if self.token.tipo in ["integer", "real"]:
        if self.token.tipo == "real":
          self.erros.append(f"real number in for, line {self.token.linha}")
        self.next()
      
      elif self.token.tipo != "nls":
        self.erros.append(f"invalid integer, line {self.token.linha}")

      #espera-se to
      if self.token.token == "to":
        self.next()
      elif self.token.tipo != "nls":
        self.erros.append(f"expected 'to' keyword, line {self.token.linha}")

      #espera-se number integer
      if self.token.tipo in ["integer", "real"]:
        if self.token.tipo == "real":
          self.erros.append(f"real number in for, line {self.token.linha}")
        self.next()
      
      elif self.token.tipo != "nls":
        self.erros.append(f"invalid integer, line {self.token.linha}")

      #espera-se do
      if self.token.token == "do":
        self.next()
      elif self.token.tipo != "nls":
        self.erros.append(f"expected 'do' keyword, line {self.token.linha}")


      self.comando()

      if self.token.token == ";":
        self.next()
    
    else:
      pass


  def ativacao_de_procedimento(self):
    if self.token.token == "(":
      self.next()
      #se já estiver fechando parênteses ele não entra em lista_de_expressoes
      if self.token.token == ")":
        self.next()
      else:
        self.lista_de_expressoes()
      
        if self.token.token == ")":
          self.next()
        else:
          self.erros.append(f") expected, {self.tokens[self.posicao-1].linha}")
  
  def lista_de_expressoes(self):
    self.expressao()
    self.lista_de_expressoes2()

  def lista_de_expressoes2(self):
    if self.token.token == ",":
      self.next()
      self.expressao()
      self.lista_de_expressoes2()

  def expressao(self):
    self.expressao_simples()

    if self.token.token in ["=", "<", ">", "<=", ">=", "<>"]:    
      self.next()
      self.expressao_simples()
      self.verificaTipoRel()
  
    

  def expressao_simples(self):
    if self.token.token in "+-":
      self.next()
    
    self.termo()
    self.expressao_simples2()

  def expressao_simples2(self):
    if self.token.token in ["+", "-", "or"]:
      token = self.token.token
      self.next()
      self.termo()
      #verificação + ou -
      if token in ["+", "-"]:
        self.verificaTipoAd()
      #verificação or
      else:
        self.verificaTipoLog()
      self.expressao_simples2()
    else:
      pass
    

  def termo(self):
    self.fator()
    self.termo2()

  def termo2(self):
    if self.token.token in ["*","/","and"]:
      token = self.token.token
      self.next()
      self.fator()
      self.termo2()

      #verificação * e /
      if token in ["*", "/"]:
        self.verificaTipoAd()
      #verificação and
      else:
        self.verificaTipoLog()
  def fator(self):
    #(expressão)
    if self.token.token == "(": 
      self.next()
      self.expressao()
      
      if self.token.token == ")":
        self.next()
      else:
        self.erros.append(f") expected, line {self.token.linha}")
    
    #real, inteiro, true ou false
    elif self.token.tipo in ["real", "integer", "boolean"]:
      self.pct.append(self.token.tipo)
      self.next()
            
    #id
    elif self.token.tipo == "id":
      tipo, declared = self.pilha.search(self.token.token)
      #Não achou na pilha de declaração
      if not declared:
        self.erros.append(f"{self.token.token} was not declared, line {self.token.linha}")
      #Achou, mas é identificador de programa
      elif tipo == "program":
        self.erros.append(f"{self.token.token} is program identifier")
        self.pct.append("erro")
      #ID declarado, vai pra tipo
      else:
        self.pct.append(tipo)


      self.next()
      #id(expressão)
      if self.token.token == "(":
        self.next()

        #se já estiver fechando parênteses ele não entra em lista_de_expressoes
        if self.token.token == ")":
          self.next()
        else:
          self.lista_de_expressoes()
          if self.token.token == ")":
            self.next()
          else:
            self.erros.append(") expected")

    #not fator
    elif self.token.token == "not":
      self.next()
      self.fator()

    else:
      self.erros.append(f"{self.token.token} Valor inválido, line {self.token.linha}")
      self.next()

  def parte_else(self):
    if self.token.token == "else":
      self.next()
      self.comando()
    #token ->  ε
    else:
      pass

  def atribuirTipo(self):
    for index in range(len(self.pilha.stack)-1, 0, -1):
        if self.pilha.stack[index]['value'] == "var_marker":
          self.pilha.stack.pop(index)
          break
        self.pilha.stack[index]['type'] = self.token.token

  def cleanScope(self):
    while self.pilha.top()['value'] != "$":
      self.pilha.pop_stack()
      #Limpa marcador
    
    self.scope -= 1
    #Limpa marcador
    self.pilha.pop_stack()
    
  #atualiza a pilha de tipo  
  def atualizaPCT(self, resultante):
    self.pct.pop()
    self.pct.pop()
    self.pct.append(resultante)

  #verifica tipo para operador aditivo ou multiplicativo
  def verificaTipoAd(self):
    if len(self.pct) > 2:
      topo = self.pct[len(self.pct)-1]
      subtopo = self.pct[len(self.pct)-2]
      if topo == "integer" and subtopo == "integer":
        self.atualizaPCT("integer")
      elif topo == "real" and subtopo == "real":
        self.atualizaPCT("real")
      elif topo == "integer" and subtopo == "real":
        self.atualizaPCT("real")
      elif topo == "real" and subtopo == "integer":
        self.atualizaPCT("real")      
      else:
        self.atualizaPCT("erro")

  #verifica operação entre booleans
  def verificaTipoLog(self):
    if len(self.pct) > 2:
      topo = self.pct[len(self.pct)-1]
      subtopo = self.pct[len(self.pct)-2]
      if topo == "boolean" and subtopo == "boolean":
        self.atualizaPCT("boolean")
      else:
        self.atualizaPCT("Invalid operation")

  #verifica operação entre operadores relacionais
  def verificaTipoRel(self):
    if len(self.pct) >= 2:
      topo = self.pct[len(self.pct)-1]
      subtopo = self.pct[len(self.pct)-2]
      if topo in ["integer", "real"] and subtopo in ["integer", "real"]:  
        self.atualizaPCT("boolean")
      else:
        self.atualizaPCT("Invalid operation")        

  #verifica subtopo e topo
  def verifySubTop(self):
    topo = self.pct[len(self.pct)-1]
    subtopo = self.pct[len(self.pct)-2]

    if topo == "integer" and subtopo == "integer":
      return True, None
    elif subtopo == "real" and topo in ["integer", "real"]:
      return True, None
    elif topo == "boolean" and subtopo == "boolean":
      return True, None
    else: 
      return False
    
  #verifica no fim de operadores relacionais se está correto
  def verificaRel(self): #True -> certo, False -> errado
    if len(self.pct) > 0:
      if self.pct[len(self.pct)-1] == "boolean":
        return True
    return False
  #limpa pilha
  def clean_stack(self):
    while(len(self.pct) != 0):
      self.pct.pop()

#Leitura dos tokens -> token | tipo
tokensFile = open("tabela2.csv", "r")
lines = tokensFile.readlines()
lines.pop(0)

#array de tokens
tokens = list()

#Adiciona tokens ao dicionário
for line in lines:
  line = line.split(" ")
  tokens.append(Token(line[0], line[1], line[2].replace("\n","")))

app = Sintatico(tokens)
app.program()

#verifica erro
if len(app.erros):
  for erro in app.erros:
    print(f'\033[31m"{erro}"\033[m')
else:
  print("A análise sintática/semântica não encontrou erros!")



