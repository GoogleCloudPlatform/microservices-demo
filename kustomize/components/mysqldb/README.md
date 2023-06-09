# Integrate Online Boutique with MySQL database

By default the `cartservice` app is serializing the data in an in-cluster Redis database. Using a database outside your GKE cluster could bring more resiliency and more security with a managed service like Amazon RDS (MySQL).

![Architecture diagram with MySQL](/docs/img/mysql.png)

## Provision a MySQL database and the supporting infrastructure

Environmental variables needed for setup. These should be set in a .bashrc or similar as some of the variables are used in the application itself. Default values are supplied in this readme, but any of them can be changed. Anything in <> needs to be replaced.

```bash
# **Note:** Primary and Read IP will need to be set after you create the instance. The command to set this in the shell is included below, but it would also be a good idea to run the command, and manually set the IP address in the .bashrc
MYSQL_HOST=<host/ip set below after instance created>
MYSQL_PORT=<port set below after instance created>
MYSQL_DATABASE=onlineboutique
MYSQL_TABLE=carts
MYSQL_USERNAME=obuser
MYSQL_PASSWORD=secret
```

To provision a MySQL database you can follow the following instructions:

```bash
docker run -d -p 3306:3306 --name onlineboutique-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=onlineboutique -e MYSQL_USER=obuser -e MYSQL_PASSWORD=secret mysql:8
```

```bash
mysql -h ${MYSQL_HOST} -u root -pmy-secret-pw -e "CREATE DATABASE ${MYSQL_DATABASE}"
mysql -h ${MYSQL_HOST} -u ${MYSQL_USERNAME} -p${MYSQL_PASSWORD} -e "CREATE TABLE ${MYSQL_TABLE} (userId char(64), productId char(64), quantity int, PRIMARY KEY(userId, productId))"  ${MYSQL_DATABASE}
mysql -h ${MYSQL_HOST} -u ${MYSQL_USERNAME} -p${MYSQL_PASSWORD} -e "CREATE INDEX cartItemsByUserId ON ${MYSQL_TABLE}(userId)" ${MYSQL_DATABASE}
```
## Deploy Online Boutique connected to a MySQL database

To automate the deployment of Online Boutique integrated with MySQL you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/mysqldb
```

_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/mysqldb
```

Update current Kustomize manifest to target this MySQL database.

```bash
MYSQL_HOST=<host/ip>
sed -i "s/MYSQL_HOST_VAL/${MYSQL_HOST}/g" components/mysqldb/kustomization.yaml
sed -i "s/MYSQL_PORT_VAL/${MYSQL_PORT:-3306}/g" components/mysqldb/kustomization.yaml
sed -i "s/MYSQL_DATABASE_VAL/${MYSQL_DATABASE}/g" components/mysqldb/kustomization.yaml
sed -i "s/MYSQL_TABLE_VAL/${MYSQL_TABLE}/g" components/mysqldb/kustomization.yaml
sed -i "s/MYSQL_USERNAME_VAL/${MYSQL_USERNAME}/g" components/mysqldb/kustomization.yaml
sed -i "s/MYSQL_PASSWORD_VAL/${MYSQL_PASSWORD}/g" components/mysqldb/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Note on MySQL connection environment variables

The following environment variables will be used by the `cartservice`, if present:

- `MYSQL_HOST`: 
- `MYSQL_PORT`: 
- `MYSQL_DATABASE`: defaults to `onlineboutique`, unless specified.
- `MYSQL_TABLE`: defaults to `carts`, unless specified.
- `MYSQL_USERNAME`: defaults to `obuser`, unless specified.
- `MYSQL_PASSWORD`: defaults to `secret`, unless specified.

## Resources
