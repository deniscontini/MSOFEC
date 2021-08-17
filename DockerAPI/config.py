##### Arquivo de configuração para o orquestrador --> orchestrator.py #####
##### Autor: Denis Contini #####
##### E-mail: denis.contini@gmail.com #####

##### Parametrização dos valores de latência (baixa, média, alta) #####
LATENCIA = {
  "l_baixa": 5.0,
  "l_alta": 80.0
}

##### Parametrização da distância lógica (quantidade de saltos) #####
HOP_DISTANCE = {
  "low": 3.0,
  "high": 11.0
}

##### Parametrização da distância geográfica (Km aproximado) #####
GEO_DISTANCE = {
  "low": 10.0,
  "high": 100.0
}

##### Parametrização das métricas de Memória e Processador (GB e Cores, respectivamente) #####
RAM = {
  "low": 4.5,
  "high": 24
}
PROC = {
  "low": 2,
  "high": 24
}

##### Parametrização do percentual de pacotes perdidos (baixa, média, alta) #####
PKG_LOSS = {
  "low": 0.2,
  "medium": 0.5,
  "high": 0.8
}

##### Parametrização do percentual de pacotes perdidos (baixa, média, alta) #####
NETWORKS = {
  "consul": 'consul',
  "edge": 'rabbitedge',
  "fog": 'rabbitfog',
  "cloud": 'rabbitcloud'
}