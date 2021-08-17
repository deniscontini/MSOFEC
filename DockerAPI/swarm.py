##### Arquivo de configuração para o orquestrador --> orchestrator.py #####
##### Autor: Denis Contini #####
##### E-mail: denis.contini@gmail.com #####

import docker
import os
import json
import time
import config
#Imports Latency
# from tcp_latency import measure_latency
from icmplib import ping, multiping, traceroute, resolve, Host, Hop
#Imports Iperf
import iperf3
#Imports Georeferenciamento/Localização
import geocoder
from geopy.geocoders import Nominatim
from geopy import distance

### Global variables ###
client = docker.from_env()
clientlow = docker.APIClient(base_url='unix://var/run/docker.sock')
ip_edge = '200.133.218.93'
ip_node = ''
latency_all = []
########################

def swarm_init():
    client.swarm.init(advertise_addr='enp3s0f1', listen_addr='enp3s0f1:2377')
    print(f'\nSwarm initialized successfully! This node is now a manager.')
    os.system('docker swarm join-token worker')

def swarm_join_worker():
    os.system('docker swarm join-token worker')

def swarm_leave():
    os.system('docker swarm leave -f')

def network_create():
    client.networks.create(config.NETWORKS['consul'], driver='overlay', attachable=True, scope='swarm')
    client.networks.create(config.NETWORKS['edge'], driver='overlay', attachable=True, scope='swarm')
    client.networks.create(config.NETWORKS['fog'], driver='overlay', attachable=True, scope='swarm')
    client.networks.create(config.NETWORKS['cloud'], driver='overlay', attachable=True, scope='swarm')

    # client.networks.create('consul', driver='overlay', attachable=True, scope='swarm')
    # client.networks.create('rabbitedge', driver='overlay', attachable=True, scope='swarm')
    # client.networks.create('rabbitfog', driver='overlay', attachable=True, scope='swarm')
    # client.networks.create('rabbitcloud', driver='overlay', attachable=True, scope='swarm')
    print('Netowrks successfully created:\n')
    networks = client.networks.list(filters={'driver': 'overlay', 'scope': 'swarm'})
    for network in networks:
        print(network.short_id, network.name)

def create_service_consul():
    os.system('docker stack deploy -c consul-compose.yml iiot')

def orchestrator(update, freq):
    node_list = client.nodes.list()
    for node in node_list:
        nodename = vars( node )["attrs"]["Description"]["Hostname"]
        noderole = vars( node )["attrs"]["Spec"]["Role"]
        nodeip = vars( node )["attrs"]["Status"]["Addr"]
        nodecpu = float(vars( node )["attrs"]["Description"]["Resources"]["NanoCPUs"])
        nodemem = int(vars( node )["attrs"]["Description"]["Resources"]["MemoryBytes"])
        ip_node = nodeip
        
        # print(f'Node Name: {node.attrs}')
        print(f'Node: {nodename} | IP:{nodeip} | Role: {noderole}')
        print('\n---Hardware Capabilities---')
        mem_node = nodemem/1000000000
        proc_node = nodecpu/1000000000
        print(f'CPU Cores: {proc_node:.0f} | Memory:{mem_node:.1f}(GB)')
        
        print('\n---Network Metrics---')

        if nodeip == '200.133.218.93':
            nodeip = '10.123.100.6'

        #qtd saltos (distância aproximada)
        hops = traceroute(nodeip)
        hop_distance = 0
        for hop in hops:
            hop_distance = hop.distance
        print(f'Distância aproximada: {hop_distance} salto(s)')

        #ping icmp
        # print('Latência ICMP')
        latencyping=ping(nodeip, count=5, timeout=2)
        latencyping.min_rtt
        lat_max = latencyping.max_rtt
        lat_min = latencyping.min_rtt
        lat_media = latencyping.avg_rtt     
        pkg_loss = latencyping.packet_loss
        pkg_sent = latencyping.packets_sent  
        print(f'Latência ICMP - Média: {lat_media:.3f}ms | Máxima: {lat_max:.3f}ms | Mínima: {lat_min:.3f}ms')
        print(f'Pacotes perdidos: {pkg_loss}')
        # l_min, l_max, l_med, list_lat = latencyMaxMedMin(lat_media)
        # list_lat.sort()
        # print(list_lat)

        #bandwidth IPERF
        # print('Largura de Banda Útil')
        cliente = iperf3.Client()
        cliente.duration=5
        cliente.server_hostname = nodeip
        cliente.port = 18080
        result = cliente.run()
        download = result.received_Mbps
        upload = result.sent_Mbps
        print(f'Largura de Banda Útil - Down: {download:.2f} Mbps | Up: {upload:.2f} Mbps')

        print('\n---Node Geolocation Metrics (Latitude, Longitude, Location, Distance)---')

        origem = geocoder.ip(ip_edge)
        destino = destino = geocoder.ip(ip_node)

        endereco_o = origem.address
        endereco_d = destino.address

        geolocator = Nominatim(user_agent="user",timeout=30)
        location_o = geolocator.geocode(origem.latlng)
        location_d = geolocator.geocode(destino.latlng)

        print(f'Localização Origem: {endereco_o}')
        print(f'Latitude | Longitude Origem: {location_o.latitude} | {location_o.longitude}')

        print(f'Endereço Destino: {endereco_d}')
        print(f'Latitude | Longitude Destino: {location_d.latitude} | {location_d.longitude}')
        
        coords_1 = (location_o.latitude, location_o.longitude)
        coords_2 = (location_d.latitude, location_d.longitude)
        distancia = distance.distance(coords_1, coords_2).km
        print(f'Distância aproximada: {distancia:.1f} Km')

        # del cliente
        # time.sleep(2)
        print()

        ##### Orquestração de containers baseado na latência entre os nós (Criação de grupos conforme a camada) #####

        node_spec_edge = {'Availability': 'active', 'Name': nodename, 'Role': noderole, 'Labels': {'layer': 'edge'}}
        node_spec_fog = {'Availability': 'active', 'Name': nodename, 'Role': noderole, 'Labels': {'layer': 'fog'}}
        node_spec_cloud = {'Availability': 'active', 'Name': nodename, 'Role': noderole, 'Labels': {'layer': 'cloud'}}

        ############# EDGE #############

        if lat_media <= config.LATENCIA["l_baixa"] and pkg_loss <= (pkg_sent * config.PKG_LOSS["low"]): ## Condição baseada na latência e qtd. de pacotes perdidos
            if mem_node <= config.RAM["low"] and proc_node <= config.PROC["low"] and hop_distance <= config.HOP_DISTANCE["low"]: ## Condição no poder de processamento do nó (CPU e RAM) e distância lógica (saltos)
                node.update(node_spec_edge)
            elif mem_node >= config.RAM["low"] and mem_node < config.RAM["high"] and proc_node >= config.PROC["low"] and proc_node < config.PROC["high"] and hop_distance > config.HOP_DISTANCE["low"] and hop_distance < config.HOP_DISTANCE["high"]:
                node.update(node_spec_fog)
            elif mem_node >= config.RAM["high"] and proc_node >= config.PROC["high"] and hop_distance >= config.HOP_DISTANCE["high"]:
                node.update(node_spec_cloud)
            else:
                print("Alguma condição não foi atendida! O nó não será considerado no cluster. Verifique as Logs!")
            #     # node.update(node_spec_edge)
        
        ############# FOG #############

        elif lat_media > config.LATENCIA["l_baixa"] and lat_media < config.LATENCIA["l_alta"] and pkg_loss <= (pkg_sent * config.PKG_LOSS["low"]): ## Condição baseada na latência e qtd. de pacotes perdidos
            if mem_node >= config.RAM["low"] and mem_node < config.RAM["high"] and proc_node >= config.PROC["low"] and proc_node < config.PROC["high"] and hop_distance > config.HOP_DISTANCE["low"] and hop_distance < config.HOP_DISTANCE["high"]: ## Condição no poder de processamento do nó (CPU e RAM) e distância lógica (saltos)
                node.update(node_spec_fog)
            elif mem_node <= config.RAM["low"] and proc_node <= config.PROC["low"] and hop_distance <= config.HOP_DISTANCE["low"]: ## Condição no poder de processamento do nó (CPU e RAM) e distância lógica (saltos)
                node.update(node_spec_edge)
            elif mem_node >= config.RAM["high"] and proc_node >= config.PROC["high"] and hop_distance >= config.HOP_DISTANCE["high"]:
                node.update(node_spec_cloud)
            else:
                print("Alguma condição não foi atendida! O nó não será considerado no cluster. Verifique as Logs!")
                # node.update(node_spec_fog)
        
        ############# CLOUD #############

        elif lat_media >= config.LATENCIA["l_alta"] and pkg_loss <= (pkg_sent * config.PKG_LOSS["low"]): ## Condição baseada na latência e qtd. de pacotes perdidos
            if mem_node >= config.RAM["high"] and proc_node >= config.PROC["high"] and hop_distance >= config.HOP_DISTANCE["high"]:
                node.update(node_spec_cloud)
            elif mem_node >= config.RAM["low"] and mem_node < config.RAM["high"] and proc_node >= config.PROC["low"] and proc_node < config.PROC["high"] and hop_distance > config.HOP_DISTANCE["low"] and hop_distance < config.HOP_DISTANCE["high"]: ## Condição no poder de processamento do nó (CPU e RAM) e distância lógica (saltos)
                node.update(node_spec_fog)
            elif mem_node <= config.RAM["low"] and proc_node <= config.PROC["low"] and hop_distance <= config.HOP_DISTANCE["low"]: ## Condição no poder de processamento do nó (CPU e RAM) e distância lógica (saltos)
                node.update(node_spec_edge)
            else:
                print("Alguma condição não foi atendida! O nó não será considerado no cluster. Verifique as Logs!")
                # node.update(node_spec_fog)

        else:
            node.update(node_spec_cloud)

        # ############# EDGE #############

        # if lat_media <= 5.0: 
        #     node.update(node_spec_edge)

        # ############# FOG #############    
        # elif lat_media > 5.0 and lat_media <= 80.0:
        #     node.update(node_spec_fog)
        
        # ############# CLOUD #############
        # elif lat_media > 80.0:
        #     node.update(node_spec_cloud)

        del cliente
        time.sleep(2)
        print()
    
    # open_ports_edge = docker.types.EndpointSpec(ports={5672: 5672, 15672: 15672, 1885: 1883})
    # open_ports_fog = docker.types.EndpointSpec(ports={5673: 5672, 15673: 15672, 1884: 1883})
    # open_ports_cloud = docker.types.EndpointSpec(ports={5674: 5672, 15674: 15672, 1883: 1883})
    
    # Criação/Atualização dos containers conforme as métricas de latência
    service_rabbit_edge()
    service_rabbit_fog()
    service_rabbit_cloud()
    print(f'Containers atualizados! Próxima leitura em {freq:.2f} s')
    print()

    # Verificação periódica das métricas (Latência e Banda útil entre os nós, update das tasks entre os gurpos)
    if update:
        time.sleep(freq)
        inspect_periodics(freq)
    
    # client.services.create('deniscontini/rabbitconsuledge:1.0', name='rabbitmq-edge', mode='global', constraints=['node.labels.layer==edge'], networks=['rabbitedge'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_edge))
    # client.services.create('deniscontini/rabbitconsulfog:1.0', name='rabbitmq-fog', mode='global', constraints=['node.labels.layer==fog'], networks=['rabbitfog'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_fog))
    # client.services.create('deniscontini/rabbitconsulcloud:1.0', name='rabbitmq-cloud', mode='global', constraints=['node.labels.layer==cloud'], networks=['rabbitcloud'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_cloud))

def service_rabbit_edge():
    service_list = client.services.list(filters={'name': 'rabbitmq-edge'})
    open_ports_edge = docker.types.EndpointSpec(ports={5672: 5672, 15672: 15672, 1885: 1883})
    if service_list:
        print("Atualizando containers na borda...")
    else:
        print("Criando serviços na Borda...")
        client.services.create('deniscontini/rabbitconsuledge:1.1', name='rabbitmq-edge', mode='global', constraints=['node.labels.layer==edge'], resources=['cpu_limit=1', 'mem_limit=1048576'], networks=[config.NETWORKS['edge']], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_edge))
        # client.services.create('deniscontini/rabbitconsuledge:1.1', name='rabbitmq-edge', mode='global', constraints=['node.labels.layer==edge'], networks=['rabbitedge'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_edge))

def service_rabbit_fog():
    service_list = client.services.list(filters={'name': 'rabbitmq-fog'})
    open_ports_fog = docker.types.EndpointSpec(ports={5673: 5672, 15673: 15672, 1884: 1883})
    if service_list:
        print("Atualizando containers na névoa...")
    else:
        print("Criando serviços na Névoa...")
        client.services.create('deniscontini/rabbitconsulfog:1.1', name='rabbitmq-fog', mode='global', constraints=['node.labels.layer==fog'], resources=['cpu_limit=1', 'mem_limit=1048576'], networks=[config.NETWORKS['fog']], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_fog))
        # client.services.create('deniscontini/rabbitconsulfog:1.1', name='rabbitmq-fog', mode='global', constraints=['node.labels.layer==fog'], networks=['rabbitfog'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_fog))

def service_rabbit_cloud():
    service_list = client.services.list(filters={'name': 'rabbitmq-cloud'})
    open_ports_cloud = docker.types.EndpointSpec(ports={5674: 5672, 15674: 15672, 1883: 1883})
    if service_list:
        print("Atualizando containers na nuvem...")
    else:
        print("Criando serviços na Nuvem...")
        client.services.create('deniscontini/rabbitconsulcloud:1.1', name='rabbitmq-cloud', mode='global', constraints=['node.labels.layer==cloud'], resources=['cpu_limit=1', 'mem_limit=1048576'], networks=[config.NETWORKS['cloud']], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_cloud))
        # client.services.create('deniscontini/rabbitconsulcloud:1.1', name='rabbitmq-cloud', mode='global', constraints=['node.labels.layer==cloud'], networks=['rabbitcloud'], env=['RABBITMQ_ERLANG_COOKIE=passwd123'], endpoint_spec=(open_ports_cloud))

def inspect_periodics(freq):
    update = True
    while update:
        print('Atualizando leituras...\n')
        orchestrator(update, freq)        

def latencyMaxMedMin(latency):
    if(latency > 0):
        latency_all.append(latency)
    l_min = min(latency_all)
    l_max = max(latency_all)
    l_med = (sum(latency_all)/len(latency_all))

    return l_min, l_max, l_med, latency_all
    
def bw_nodes():
    node_list = client.nodes.list()
    for node in node_list:
        nodename = vars( node )["attrs"]["Description"]["Hostname"]
        nodeip = vars( node )["attrs"]["Status"]["Addr"]
        print(f'Node: {nodename} | IP:{nodeip}')
        #bandwidth IPERF
        print('Largura de Banda Útil')
        cliente = iperf3.Client()
        cliente.duration=3
        cliente.server_hostname = nodeip
        cliente.port = 18080
        result = cliente.run()
        download = result.received_Mbps
        upload = result.sent_Mbps
        print(f'Down: {download:.2f} Mbps | Up: {upload:.2f} Mbps')
        del cliente
        time.sleep(2)

# def function():
#     node_list = client.nodes.list()
#     for node in node_list:
#         nodename = vars( node )["attrs"]["Description"]["Hostname"]
#         nodeip = vars( node )["attrs"]["Status"]["Addr"]
#         print(f'Node: {nodename} | IP:{nodeip}')

def latency_teste():
    node_list = client.nodes.list()
    for node in node_list:
        nodename = vars( node )["attrs"]["Description"]["Hostname"]
        noderole = vars( node )["attrs"]["Spec"]["Role"]
        nodeip = vars( node )["attrs"]["Status"]["Addr"]
        print(f'Node: {nodename} | IP:{nodeip} | Role: {noderole}')
        print('\n---Network Metrics---')
        if nodeip == '200.133.218.93':
            nodeip = '10.123.100.6'
        latencyping=ping(nodeip, count=5, timeout=2)
        latencyping.min_rtt
        lat_max = latencyping.max_rtt
        lat_min = latencyping.min_rtt
        lat_media = latencyping.avg_rtt
        pkg_loss = latencyping.packet_loss   
        pkg_sent = latencyping.packets_sent  
        print(f'Latência ICMP - Média: {lat_media:.3f}ms | Máxima: {lat_max:.3f}ms | Mínima: {lat_min:.3f}ms')
        print(f'Pacotes perdidos: {pkg_loss} | {pkg_sent}')
        x, y, z, list_lat = latencyMaxMedMin(lat_media)
        print(x)
        print(y)
        print(z)
        list_lat.sort()
        print(list_lat)

def geolocation():
    print('\n---Node Geolocation Metrics (Latitude, Longitude, Location, Distance)---')

    origem = geocoder.ip(ip_edge)
    # destino = destino = geocoder.ip('177.51.66.79')
    destino = destino = geocoder.ip('177.154.39.158')
    # destino = destino = geocoder.ip('143.106.73.65')
    # destino = destino = geocoder.ip('128.110.153.107')

    endereco_o = origem.address
    endereco_d = destino.address

    geolocator = Nominatim(user_agent="user",timeout=10)
    location_o = geolocator.geocode(endereco_o)
    location_d = geolocator.geocode(endereco_d)
    # location_o = geolocator.geocode(origem.latlng)
    # location_d = geolocator.geocode(destino.latlng)

    print(f'Endereço Origem: {endereco_o}')
    print(f'Latitude | Longitude Origem: {location_o.latitude} | {location_o.longitude}')

    print(f'Endereço Destino: {endereco_d}')
    print(f'Latitude | Longitude Destino: {location_d.latitude} | {location_d.longitude}')
        
    coords_1 = (location_o.latitude, location_o.longitude)
    coords_2 = (location_d.latitude, location_d.longitude)
    distancia = distance.distance(coords_1, coords_2).km
    print(f'Distância aproximada: {distancia:.1f} Km')


print('Escolha uma das opções abaixo:\n')
print('1 - Iniciar docker swarm;\n')
print('2 - Juntar-se como worker;\n')
print('3 - Deixar o cluster;\n')
print('4 - Criar Rede Overlay;\n')
print('5 - Criar stack consul (service swarm);\n')
# print('6 - Criar container Rabbit (service swarm);\n')
print('6 - Métricas de Rede (Latência e Banda);\n')
print('7 - Verificação periódica;\n')
print('8 - Largura Banda/IPERF;\n')
print('9 - Geolocation\n')
print('10 - List\n')
menu = int(input())

if menu == 1:
    swarm_init()
elif menu == 2:
    swarm_join_worker()
elif menu == 3:
    swarm_leave()
elif menu == 4:
    network_create()
elif menu == 5:
    create_service_consul()
# elif menu == 6:
#     create_service_rabbitmq()
elif menu == 6:
    orchestrator(False, 0)
elif menu == 7:
    print('Com qual frequência deseja inspecionar os nós:')
    frequencia = int(input())
    print()
    orchestrator(True, frequencia)
elif menu == 8:
    bw_nodes()
elif menu == 9:
    geolocation()
elif menu == 10:
    latency_teste()
else:
    print('Opção inexistente!')