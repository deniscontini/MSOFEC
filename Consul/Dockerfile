FROM consul:latest

ENTRYPOINT [""]

COPY ./cluster.sh ./cluster.sh

RUN chmod +x cluster.sh

# RUN consul agent -server -bootstrap-expect=1 -retry-max=3 -retry-interval=10s -data-dir=/var/consul -datacenter=iiot -join=consul -retry-join=consul -bind='{{ GetInterfaceIP \"eth0\" }}' -client=0.0.0.0 -ui

# CMD  ["consul", "agent", "-server", "-bootstrap-expect=1", "-retry-max=3", "-retry-interval=10s", "-data-dir=/var/consul", "-datacenter=iiot", "-join=consul", "-retry-join=consul", "-bind='{{ GetInterfaceIP \"eth0\" }}'", "-client=0.0.0.0", "-ui"]

CMD  ["./cluster.sh"]