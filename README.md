# BlackCat
🐈🎃 _Dependencies can be spooky!_ 🎃🐈

BlackCat is a tool for the centralization of github dependency scanning outputs, mainly through output to splunk, which allows for
better tracking and reporting at an organizational level using GitHub's dependency scanning functionality.
## Setup and Installation
### Configuration
Before you begin, you'll need to enable dependency scanning for any repos you want reports on. To do this, I recommend using github's tool:  
https://github.com/github/enable-security-alerts-sample  
(may generate a lot of emails for larger organizations)  
Once you've done this, there's a few pieces of information blackcat needs:  
1. A github token for accessing dependencies. This will require `read:org` and `repo` 
permissions on an account with visibility to your security vulnerabilities (likely an admin).
2. (Optional) A token for splunks' HTTP Event Collectors (HECs)
  
You should put these two items in the config.yml(see config.example.yml for reference) file, along with any other additional options
If you're using kubernetes, put these values in `k8s/secrets.yml` instead.

### Deployment Info   

Now that you've configured BlackCat, it can be deployed in a few ways:
1. Using pythons' pipenv
2. Using Docker
3. Using kubernetes

#### Using Pipenv
1. Install pipenv: `pip install pipenv`
2. Install the dependencies (from within the project directory): `pipenv install`
3. Run: `pipenv run python main.py`

#### Using Docker
1. Install docker
2. Build the image using `docker build -t blackcat:v1 .`
3. Run! `docker run blackcat:v1`

#### Using Kubernetes
_This assumes a basic knowledge of kubernetes, as well as an existing cluster and registry._
1. Go through the steps described in the `Using Docker` section above and publish that image to your container registry 
2. Modify `k8s-cron.spec` to run at whatever interval you want (Defaults to every day at 15:00:00)
3. Put your secrets in `secrets.yml` ([More Info](https://kubernetes.io/docs/concepts/configuration/secret/))
4. Run `kubectl apply -f  ./k8s/secrets.yml`
5. Run `kubectl create -f ./k8s/k8s-cron.spec`