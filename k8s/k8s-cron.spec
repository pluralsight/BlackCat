apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: blackcat
spec:
  schedule: "0 15 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: blackcat
              image: pssecops/blackcat
              args: []
              resources:
                requests:
                  memory: "256Mi"
                  cpu: "250m"
                limits:
                  memory: "512Mi"
                  cpu: "500m"
              env:
                - name: SPLUNK_HEC
                  valueFrom:
                    secretKeyRef:
                      name: blackcat-secret
                      key: splunk_hec

                - name: ORG_NAMES
                  valueFrom:
                    secretKeyRef:
                      name: blackcat-secret
                      key: org_names

                - name: GIT_TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: blackcat-secret
                      key: git_token
          restartPolicy: OnFailure
