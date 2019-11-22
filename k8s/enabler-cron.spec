apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: blackcat-enable
spec:
  schedule: "0 0 * * 4"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: blackcat
              image: pssecops/blackcat
              args:
                - "--enable"
              resources:
                requests:
                  memory: "256Mi"
                  cpu: "250m"
                limits:
                  memory: "512Mi"
                  cpu: "500m"
              env:
                - name: SPLUNK_PORT
                  valueFrom:
                    secretKeyRef:
                      name: blackcat-secret
                      key: splunk_port

                - name: SPLUNK_DOMAIN
                  valueFrom:
                    secretKeyRef:
                      name: blackcat-secret
                      key: splunk_domain

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
