#!/bin/bash

project_list="gcp_project_lists.txt"
log_file="gclb_detail_list.txt"

get_gclb() {
    local project=$1

    # target_http_proxy=$(gcloud compute target-http-proxies list --project "${project}")
    # target_https_proxy=$(gcloud compute target-http-proxies list --project "${project}")
    url_maps=$(gcloud compute url-maps list --project ${project} --format="csv[no-heading,separator='|'](name,hostRules.hosts,pathMatchers.defaultService,pathMatchers.name,defaultService)" --quiet)
    
    if [ -n "$(echo "$url_maps" | tr -d '[:space:]')" ]; then
        while IFS= read -r url_map; do
            backend=$(echo $url_map | awk -F'|' '{print $5}')
            backend_name=$(echo $backend | awk -F'/' '{ print $2 }') 
            url_map_name=$(echo $url_map | awk -F'|' '{print $1}')
            # echo $url_map_name

            if [[ $backend == backendBuckets* ]]; then
                backend_result=$(gcloud compute backend-buckets list --project ${project} --filter="name ~ $backend_name" --format="csv[no-heading,separator='|'](name,bucketName)")
            elif [[ $backend == backendServices* ]]; then
                backend_result=$(gcloud compute backend-services list --project ${project} --format="csv[no-heading,separator='|'](name,backends)")
            fi

            target_proxy=$(gcloud compute target-https-proxies list --project ${project} --format="csv[no-heading](name)" --filter="urlMap ~ $url_map_name")

            if [[ $backend == "" ]]; then
               backend_result=""
            fi

            if [ -n "$(echo "$target_proxy" | tr -d '[:space:]')" ]; then
                frontend_result=$(gcloud compute forwarding-rules list --project ${project} --filter="target ~ $target_proxy" --format="csv[no-heading,separator='|'](name,IPAddress,networkTier)")
                echo "$project|$url_map|$backend_result|$frontend_result"
                echo "$project|$url_map|$backend_result|$frontend_result" >> ${log_file}
            else 
                echo "No forwarding rules found for url map: $url_map_name"
            fi
        done <<< "$url_maps"
        
    else
        echo "No GCLB found on project: $project"
    fi
}


for project in $(cat $project_list);
do
    get_gclb "$project" 
    # result
    # project, gclb name, backend, ip address
done
