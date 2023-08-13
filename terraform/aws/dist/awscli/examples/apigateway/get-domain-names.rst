**To get a list of custom domain names**

Command::

  aws apigateway get-domain-names

Output::

  {
      "items": [
          {
              "distributionDomainName": "d9511k3l09bkd.cloudfront.net", 
              "certificateUploadDate": 1452812505, 
              "certificateName": "my_custom_domain-certificate", 
              "domainName": "subdomain.domain.tld"
          }
      ]
  }
