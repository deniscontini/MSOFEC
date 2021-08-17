import docker 

client = docker.from_env()

def print_all_containers():
        container_list = client.containers.list()
        for container in container_list:
            print(f'Container ID: {container.id}')
            print(f'Container Short ID: {container.short_id}')
            print(f'Container Name: {container.name}')
            print(f'Container status: {container.status}')
            print()

def get_containers_running():
    container_list = client.containers.list(filters={'status': 'running'})
    if container_list:
        return container_list


def remove_all_containers_running(): 
    containers_list = get_containers_running()
    if containers_list:
        for container in containers_list:
            try:
                print(f'Try remove container {container.name}')
                container.remove(force=True)
                print(f'Container called {container.name} sucessfully removed')
            except Exception as err:
                print(f'Failed to remove the container named {container.name}\nErro: {err}')

def action_container(containerid, action):
    if action.lower() in ['start', 'stop']:
        try:
            container = client.containers.get(containerid)
            try:
                result = getattr(container, action)()
                print(f'Container call {container.name} successfully {action}!')
            except Exception as err:
                print(f'Failed to {action} the container {container.name}')
        except docker.errors.NotFound:
            print(f'Container does not exist!')
    else:
        print('Invalid action!')

action_container('a3efb7d91b2a','dump')