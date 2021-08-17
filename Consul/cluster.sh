#!/bin/sh

ip=$(ip addr show | grep global | grep -oE '((1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.){3}(1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])' | sed -n '5p')

consul agent -server -bootstrap-expect=1 -retry-max=3 -retry-interval=10s -data-dir=/var/consul -datacenter=iiot -join=consul -retry-join=consul -bind=$ip -client=0.0.0.0 -ui