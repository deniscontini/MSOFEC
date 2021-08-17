FROM rabbitmq:3-management

COPY rabbitmq.conf /etc/rabbitmq/
COPY definitions.json /etc/rabbitmq/

RUN rabbitmq-plugins --offline enable rabbitmq_mqtt rabbitmq_peer_discovery_consul rabbitmq_federation rabbitmq_federation_management rabbitmq_shovel rabbitmq_shovel_management rabbitmq_top

EXPOSE 1883