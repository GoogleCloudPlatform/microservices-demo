# Provision a fully managed Redis Enterprise database in Google Cloud Marketplace


1. Subscribe to Redis Enterprise in Google Cloud Marketplace.
Look up and locate **Redis Enterprise Cloud Flexible - Pay as You Go** in Google Cloud Marketplace.  Once you are on the product page, click **SUBSCRIBE**
![Subscribe to GCP MP - 1](/docs/img/redis-enterprise/GCP_MP_01.png)
Review the Terms and click **SUBSCRIBE**
![Subscribe to GCP MP - 2](/docs/img/redis-enterprise/GCP_MP_02.png)
Click **GO TO PRODUCT PAGE** in the pop-up window
![Subscribe to GCP MP - 3](/docs/img/redis-enterprise/GCP_MP_03.png)
Click **MANAGE ON PROVIDER**
![Subscribe to GCP MP - 4](/docs/img/redis-enterprise/GCP_MP_04.png)
Click **OK** and it will bring you to Redis Enterprise Cloud page
![Subscribe to GCP MP - 5](/docs/img/redis-enterprise/GCP_MP_05.png)

1. Create a Redis Enterprise database instance.
In our case, we use an existing gmail email account to log into Redis Enterprise Cloud
![Create DB in GCP MP - 1](/docs/img/redis-enterprise/GCP_MP_06.png)
![Create DB in GCP MP - 2](/docs/img/redis-enterprise/GCP_MP_07.png)
Click **Map account** to map the newly created GCP Marketplace subscription
![Create DB in GCP MP - 3](/docs/img/redis-enterprise/GCP_MP_08.png)
Click **+ New subscription** to create a new Redis Enterprise Cluster subscription
![Create DB in GCP MP - 4](/docs/img/redis-enterprise/GCP_MP_09.png)
Select **Flexible plans**
![Create DB in GCP MP - 5](/docs/img/redis-enterprise/GCP_MP_10.png)
Choose **Google Cloud Platform**, select a GCP region and provide a name for your subscription. Then click **Continue**
![Create DB in GCP MP - 6](/docs/img/redis-enterprise/GCP_MP_11.png)
Click the **+** sign to create a new database
![Create DB in GCP MP - 7](/docs/img/redis-enterprise/GCP_MP_12.png)
Create a new database as shown in the screen shot below. Then click **Save database**
![Create DB in GCP MP - 8](/docs/img/redis-enterprise/GCP_MP_13.png)
Then click **Continue**
![Create DB in GCP MP - 9](/docs/img/redis-enterprise/GCP_MP_14.png)
Review your subscription settings and click **Create subscription**
![Create DB in GCP MP - 10](/docs/img/redis-enterprise/GCP_MP_15.png)
It will take about 5 minutes to complete
![Create DB in GCP MP - 11](/docs/img/redis-enterprise/GCP_MP_16.png)
Copy the **Private endpoint** information for later use
![Create DB in GCP MP - 13](/docs/img/redis-enterprise/GCP_MP_17.png)
Copy the **Default user password** information for later use
![Create DB in GCP MP - 14](/docs/img/redis-enterprise/GCP_MP_18.png)


1. Peer your VPC with Redis's managed VPC.
Select **Connectivity** tab as follows. Then click **+ Add peering**
![VPC Peering in GCP MP - 1](/docs/img/redis-enterprise/GCP_MP_19.png)
Provide the **Project ID** and **Network name** your GKE cluster belongs to. Then follow the on-screen instructions to run the provided **Google cloud command**
![VPC Peering in GCP MP - 2](/docs/img/redis-enterprise/GCP_MP_20.png)
It will take a couple minutes to complete peering
![VPC Peering in GCP MP - 3](/docs/img/redis-enterprise/GCP_MP_21.png)

  
Important notes:
- You cannot connect to a fully managed Redis Enterprise database (redis) instance via private endpoint from a GKE cluster without peering your VPC to Redis's managed VPC.
