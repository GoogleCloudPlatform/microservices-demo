IMAGS=`cat release/kubernetes-manifests.yaml | grep image | awk '{print $2}'`
array=($IMAGS)
for IMAG in "${array[@]}"
do
	echo "begin to pull $IMAG"
	docker pull $IMAG
	CRIMG=`echo $IMAG | awk -F'/' '{print $NF}'`
    LI="cr-cn-beijing.volces.com/hackathon/$CRIMG"
	echo $LI
	docker tag $IMAG $LI
	docker push $LI
done
