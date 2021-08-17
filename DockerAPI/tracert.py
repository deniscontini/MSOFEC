from icmplib import ping, multiping, traceroute, resolve, Host, Hop

# hops = traceroute('192.168.0.1')
# hops = traceroute('200.133.218.93')
# hops = traceroute('143.106.73.65')
hops = traceroute('ms0844.utah.cloudlab.us')

# ip = '192.168.0.1'
# ip = '200.133.218.93'
# ip = '143.106.73.65'
ip = 'ms0844.utah.cloudlab.us'

print('Distance/TTL         Address         Average round-trip time')
last_distance = 0

for hop in hops:
    if last_distance + 1 != hop.distance:
        print('Some gateways are not responding')
    # See the Hop class for details
    print(f'{hop.distance}          {hop.address}           {hop.avg_rtt} ms')
    last_distance = hop.distance

print('Latência ICMP')
latencyping=ping(ip, count=5, timeout=2)
latencyping.min_rtt
lat_max = latencyping.max_rtt
lat_min = latencyping.min_rtt
lat_media = latencyping.avg_rtt     
print(f'Latência Média: {lat_media:.3f}ms | Latência Máxima: {lat_max:.3f}ms | Latência Mínima: {lat_min:.3f}ms')

x = len(hops)
# qtd_saltos = {hops.distance[x-1]}
print(f'Qtde. aproximada de saltos de distância: {last_distance} salto(s)\n')