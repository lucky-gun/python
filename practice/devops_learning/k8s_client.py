from kubernetes import client
from kubernetes import config

config.load_kube_config()

v1 = client.CoreV1Api()

pod_list = v1.list_pod_for_all_namespaces()
node_list = v1.list_node()


print("=" * 60)
print("Kubernetes Pod Explorer")
print("=" * 60)

for pod in pod_list.items:

    print(f"\n{'-' * 60}")

    print(f"Name            : {pod.metadata.name}")
    print(f"Namespace       : {pod.metadata.namespace}")
    print(f"Phase           : {pod.status.phase}")
    print(f"Node            : {pod.spec.node_name}")
    print(f"Pod IP          : {pod.status.pod_ip}")
    print(f"Host IP         : {pod.status.host_ip}")

    print("\nContainers")

    for container in pod.spec.containers:

        print(f"  - Name        : {container.name}")
        print(f"    Image       : {container.image}")

    print("\nContainer Status")

    for status in pod.status.container_statuses or []:

        print(f"  - Ready       : {status.ready}")
        print(f"    Restart     : {status.restart_count}")

    print("\nLabels")

    for key, value in pod.metadata.labels.items():
        print(f"  {key} = {value}")

    print("\nAnnotations")

    for key, value in (pod.metadata.annotations or {}).items():
        print(f"  {key} = {value}")

print("\n")
print("=" * 60)
print("Node Information")
print("=" * 60)

for node in node_list.items:

    print(f"\n{'-' * 60}")

    print(f"Node : {node.metadata.name}")

    print("\nConditions")

    for condition in node.status.conditions:

        print(
            f"  {condition.type:<20} : {condition.status}"
        )
