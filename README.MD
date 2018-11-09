A *Python* app which target to demo how to use AMQP to connect to a solace instance in the cloud foundry platform.

The app use the paho lib, so add [qpid proton](https://qpid.apache.org/) in your *requirements.txt*

**How to use it:**

- Download and push the app to the cloud foundry platform.
- Provision and solace instance and bind to the app.
- Restart/Restage the app.

**How to test it:**

The app contains to url,

- http://{link_to_app}/amqp/solace/queue, this will use the solace SEMP v2 to create a new durable queue which is : python-amqp-solace-queue.
- http://{link_to_app}/amqp/solace/subscribe publish 6 messages to the queue: _python-amqp-solace-queue_
- http://{link_to_app}/amqp/solace/subscribe subscribe 6 messages the queue: _python-amqp-solace-queue_

and check the app log and the connections in the soladmin/gui to verify.
 
To create the queue:

```python
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
```

How to publish messages, check the code under producer.py

How to subscribe messages, check the consumer.py