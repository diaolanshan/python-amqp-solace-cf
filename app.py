from flask import Flask
import os
import json
from consumer import Recv
from producer import MessageProducer
from proton.reactor import Container
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.config.from_object(__name__)

port = int(os.getenv('VCAP_APP_PORT', 8080))

queue_name = 'python-amqp-solace-queue'

vcap_services = json.loads(os.environ['VCAP_SERVICES'])
if vcap_services != None:
    for service in vcap_services.keys():
        if 'solace-pubsub' in vcap_services[service][0]['tags']:
            management_host = 'http://' + vcap_services[service][0]['credentials']['activeManagementHostname']
            management_username = vcap_services[service][0]['credentials']['managementUsername']
            management_password = vcap_services[service][0]['credentials']['managementPassword']
            msg_vpn = vcap_services[service][0]['credentials']['msgVpnName']
            client_username = vcap_services[service][0]['credentials']['clientUsername']
            client_password = vcap_services[service][0]['credentials']['clientPassword']
            uris = vcap_services[service][0]['credentials']['amqpUris']
            break


@app.route('/amqp/solace/queue', methods=['GET', 'POST'])
def define_queue():
    #use the management username password to auth the app
    auth = HTTPBasicAuth(management_username, management_password)

    request_body = {
        "queueName": queue_name,
        "accessType": "non-exclusive",
        "permission": "consume",
        "ingressEnabled": True,
        "egressEnabled": True
    }
    response = requests.post(url=management_host + '/SEMP/v2/config/msgVpns/{}/queues'.format(msg_vpn),
                             json=request_body,
                             auth=auth)

    return 'Queue created successfully' if response.status_code == 200 else 'Error while create queue, reason:'.format(
        response.reason)


@app.route('/amqp/solace/publish')
def publish_message():
    producer = MessageProducer(uris, queue_name, 6, client_username, client_password)
    Container(producer).run()
    return 'OK', 200


@app.route('/amqp/solace/subscribe')
def subscribe_message():
    subscriber = Recv(uris, queue_name, 6, client_username, client_password)
    Container(subscriber).run()
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
