#sudo apt install npm
#npm install -g newman
#npm install -g newman-reporter-xunit
#newman run sealights\ excersise.postman_collection.json --env-var machine_dns=$machine_dns
newman run sealights-excersise.postman_collection.json --env-var machine_dns=$machine_dns -r xunit --reporter-xunit-export './result.xml'