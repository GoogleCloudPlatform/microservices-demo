## Steps to setup Online Boutique App with Datadog monitoring 

### Steps to install the boutique app on local machine with Kubernetes enabled on docker-desktop

	1. Clone the source code for the online boutique app
	$ git clone git@github.com:Relyance/microservices-demo.git
	
	2. Once the source code is cloned, enter the folder containing the source code
	$ cd microservices-demo/release
	
	3. Run the kubernetes apply command to run the online boutique app
	$ kubectl apply -f kubernetes-manifests.yaml
	(Note: Wait for 10 minutes for the whole app to be downloaded and up and running
	
	4. Do the port-forwarding to run the application from the browser
   $ kubectl port-forward service/frontend 8080:80 


### Steps to setup Datadog agent for monitoring Online Boutique App (deployed as Kubernetes) [Explained above]

	1. Configure agent permissions
	$ kubectl apply -f "https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/rbac/clusterrole.yaml"
	$ kubectl apply -f "https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/rbac/serviceaccount.yaml"
	$ kubectl apply -f "https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/rbac/clusterrolebinding.yaml"
	
	2. Create a secret that contains your Datadog API Key
	$ kubectl create secret generic datadog-agent --from-literal api-key="77ed0972ca94340f9db3fb78ee5e89cc" --namespace="default"
	
	1. Enable the datadog agent manifest file 
	$ kubectl apply -f datadog-agent-logs-apm.yaml
