from absl import app
from absl import flags
import re
import yaml
import json
from uuid import uuid4
from math import ceil
import random
from copy import deepcopy

FLAGS = flags.FLAGS

# Lower bound is 2 because why would you want to test without any traffic?
flags.DEFINE_multi_string(
    'service', None,
    'Service definition of the form {count}x{pod_count}[-{latency:(low|med|high|var)}]'
)
flags.DEFINE_integer(
    'connections_per_service', None,
    'The number of outgoing services each service should query')
flags.DEFINE_bool(
    'focus_calls', False,
    'If set, all requests are focused on the same set of services.')
flags.DEFINE_integer(
    'focus_sources', -1,
    'If set to >= 0, all requests will come from the same set of services (that number).'
)
flags.DEFINE_bool('no_istio', False,
                  'If true, disables istio sidecar injection.')
flags.DEFINE_bool('no_crash_on_fail', False,
                  'If true, disables crashing clients as a way to notify of call failures.')
flags.DEFINE_integer('poll_start_delay', 60,
                     'Delay in seconds before clients start querying.')
flags.DEFINE_integer('low_latency_ms', 0,
                     'The average ms delay for low latency services')
flags.DEFINE_integer('med_latency_ms', 50,
                     'The average ms delay for med latency services')
flags.DEFINE_integer('high_latency_ms', 5000,
                     'The average ms delay for high latency services')
flags.DEFINE_integer('normal_latency_stddev', 0,
                     'The normal latency ms standard deviation.')
flags.DEFINE_integer('var_latency_ms', 200,
                     'The average ms delay for variable latency services')
flags.DEFINE_integer('var_latency_stddev', 10,
                     'The stddev ms delay for variable latency services')
flags.DEFINE_string('workload_server_image_path',
                    'gcr.io/lesser-weevil/server:v1',
                    'GCR path to the workload server image')
flags.DEFINE_string('workload_client_image_path',
                    'gcr.io/lesser-weevil/client:v1',
                    'GCR path to the workload client image')
flags.DEFINE_integer('workload_server_port', '8080',
                     'Port to expose from the workload server image.')
flags.DEFINE_float('qps_per_edge', 0.1,
                   'QPS for every pairing of pod to service.')

flags.mark_flag_as_required('service')
flags.mark_flag_as_required('connections_per_service')
flags.register_validator(
    'service',
    lambda value: all([parse_service(v) is not False for v in value]),
    message='Invalid service pattern')

SERVICE_PATTERN = r'^(\d+)x(\d+)(?:-(\w+))?$'

NAMESPACE = 'mesh-load-test-ns'

CONFIG_SEPARATOR = '\n---\n'

# kubectl get deployments --all-namespaces -o custom-columns=NAME:.metadata.name,REPLICAS:.spec.replicas,CPU:.spec.template.spec.containers[*].resources.requests.cpu,MEM:.spec.template.spec.containers[*].resources.requests.memory,CPU_LIM:.spec.template.spec.containers[*].resources.limits.cpu,MEM_LIM:.spec.template.spec.containers[*].resources.limits.memory

NODE_AVAIL_mCPU = 1930 - 100 - 1 - 100  # allocatable - daemon_used
ISTIO_USED_mCPU = 10 + 10 + 100 + 500 + 100 + 10 + 100 + 10 + 1000 + 100 + 10 + 13 + 50 + (
      100 + 150 + 10) * 2 + 20 + 10 + 43 + 5 + 40
DEFAULT_WORKLOAD_mCPU = 100

NODE_AVAIL_MEM_Mi = 5642 - 20 - 200  # allocatable - daemon_used
ISTIO_USED_MEM_Mi = 128 + 2048 + 128 + 128 + 1024 + 128 + 120 + 91 + (
      70 + 20 + 20) * 2 + 10 + 20 + 55 + 50 + 50
DEFAULT_WORKLOAD_MEM_Mi = 140

used_rand_chars = set()


def get_rand_chars(length):
  while True:
    ret = uuid4().urn[-length - 1:-1].lower()
    if ret not in used_rand_chars:
      used_rand_chars.add(ret)
      return ret


class Namespace:

  def __init__(self, name):
    self.name = name

  def get_namespace_yaml(self):
    res = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': self.name,
            'labels': {
                'istio-injection':
                  ('enabled' if not FLAGS.no_istio else 'disabled'),
            },
        }
    }
    return yaml.dump(res)


class Service:

  def __init__(self, pods, latency, latency_str):
    # Name format ultimately ends up as:
    # {latency}{num_pods}-{outgoing_connections}-{incoming_connections}
    self.name = '%s%s' % (latency_str[0], pods)
    self.pods = pods
    self.latency = latency
    self.latency_str = latency_str
    self.namespace = NAMESPACE
    self.num_callers = 0
    self.services_to_call = []

  def _get_workload_config(self):
    res = {
        'name': self.name,
        'responses': {
            '200': 0.98,
            '400': 0.02,
        },
        'clients': [{
            'service': service.name,
            'qps': FLAGS.qps_per_edge,
        } for service in self.services_to_call],
        'startDelay': FLAGS.poll_start_delay,
        'crashOnFail': not FLAGS.no_crash_on_fail,
    }
    return json.dumps(res)

  def get_deployment_yaml(self):
    res = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': self.name,
            'namespace': self.namespace,
            'labels': {
                'app': self.name,
            },
        },
        'spec': {
            'replicas': self.pods,
            'selector': {
                'matchLabels': {
                    'app': self.name,
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': self.name,
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'server',
                        'image': FLAGS.workload_server_image_path,
                        'ports': [{
                            'containerPort': FLAGS.workload_server_port,
                            'name': 'http-port',
                        }],
                        'env': [{
                            'name': 'MESH_GENERATOR_CONFIG',
                            'value': self._get_workload_config()
                        }, ],
                        'resources': {
                            'requests': {
                                'cpu': '20m',
                                'memory': '300Mi'
                            },
                        },
                    }, {
                        'name':
                          'client',
                        'image':
                          FLAGS.workload_client_image_path,
                        'env': [{
                            'name': 'MESH_GENERATOR_CONFIG',
                            'value': self._get_workload_config()
                        }, ],
                    }],
                }
            },
        },
    }
    return yaml.dump(res)

  def get_service_yaml(self):
    res = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': self.name,
            'namespace': self.namespace,
            'labels': {
                'app': self.name,
            },
        },
        'spec': {
            'selector': {
                'app': self.name,
            },
            'ports': [{
                'protocol': 'TCP',
                'port': 80,
                'targetPort':
                  'http-port',  # Keep in sync with deployment port label above.
                'name': 'http',  # Must match Istio naming schemes
            }],
        }
    }
    return yaml.dump(res)


def parse_service(service_str):
  m = re.search(SERVICE_PATTERN, service_str)
  if not m:
    print('Invalid pattern for service: `%s`' % service_str)
    return False
  count = int(m.group(1))
  pods = int(m.group(2))
  latency_str = m.group(3)

  if latency_str is None:
    # Default to low
    latency_str = 'low'

  latency_avg = None
  latency_stddev = None
  if latency_str == 'low':
    latency_avg = FLAGS.low_latency_ms
    latency_stddev = FLAGS.normal_latency_stddev
  elif latency_str == 'med':
    latency_avg = FLAGS.med_latency_ms
    latency_stddev = FLAGS.normal_latency_stddev
  elif latency_str == 'high':
    latency_avg = FLAGS.high_latency_ms
    latency_stddev = FLAGS.normal_latency_stddev
  elif latency_str == 'var':
    latency_avg = FLAGS.var_latency_ms
    latency_stddev = FLAGS.var_latency_stddev
  else:
    print('Invalid latency type in pattern: `%s`' % latency_str)
    return False

  return count, Service(pods, (latency_avg, latency_stddev), latency_str)


def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  output_config = []
  output_config.append(Namespace(NAMESPACE).get_namespace_yaml())

  total_services = 0
  total_pods = 0
  services = []
  for service_str in FLAGS.service:
    count, service = parse_service(service_str)
    for i in range(0, count):
      total_services += 1
      total_pods += service.pods
      name = '%s' % get_rand_chars(4)
      cur_service = deepcopy(service)
      cur_service.name += '-%s' % get_rand_chars(4)
      services.append(cur_service)
  k = min(FLAGS.connections_per_service, len(services))
  focus_services = None
  if FLAGS.focus_calls:
    focus_services = random.sample(services, k)
  focus_sources = None
  if FLAGS.focus_sources >= 0:
    focus_sources = random.sample(services, FLAGS.focus_sources)
  for service in services:
    local_k = k
    if focus_sources is not None and service not in focus_sources:
      local_k = 0

    services_to_call = random.sample(
        services, local_k) if focus_services is None else focus_services
    service.name += '-%s' % len(services_to_call)
    service.services_to_call = services_to_call
    for callee in services_to_call:
      callee.num_callers += 1
  for service in services:
    service.name += '-%s' % service.num_callers
  for service in services:
    output_config.append(service.get_deployment_yaml())
    output_config.append(service.get_service_yaml())

  nodes_needed_for_cpu = int(
      ceil((ISTIO_USED_mCPU + total_pods * DEFAULT_WORKLOAD_mCPU + 100) /
           NODE_AVAIL_mCPU))
  nodes_needed_for_mem = int(
      ceil((ISTIO_USED_MEM_Mi + total_pods * DEFAULT_WORKLOAD_MEM_Mi + 100) /
           NODE_AVAIL_MEM_Mi))

  print(max(nodes_needed_for_cpu, nodes_needed_for_mem))
  print(CONFIG_SEPARATOR.join(output_config))


if __name__ == '__main__':
  app.run(main)
