#!/opt/homebrew/bin/zsh
## getcert -n namespace -s secret

# SECRET_NAME=$3
# NAMESPACE=$1
INDEX=0



Help()
{
   # Display Help
   echo "Getcert is simple script to get information from certificate that stored in Kubernetes TLS Secret."
   echo
   echo "Syntax: getcert [-n|h|s]"
   echo "options:"
   echo "-n     Specify the namespace."
   echo "-s     Specify the secret name."
   echo "-h     Print this Help."
   echo
}

if [ -z "$1" ]
then
    Help
    exit 1;
fi

while getopts ":hn:s:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      n) # Enter a name
         NAMESPACE=$OPTARG
         ;;
      s)
         SECRET_NAME=$OPTARG
         ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

kubectl get secret -n $NAMESPACE $SECRET_NAME -o yaml | yq '.data."tls.crt"' | base64 -d > /tmp/${SECRET_NAME}.crt
openssl x509 -noout -in /tmp/${SECRET_NAME}.crt -subject -ext subjectAltName -fingerprint -issuer -dates
