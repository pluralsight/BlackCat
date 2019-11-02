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
            image: blackcat
            args: []
            env:
              - name: SPLUNK_HEC
                valueFrom:
                  secretKeyRef:
                    name: blackcat-secret
                    key: splunk_hec
              - name: GIT_TOKEN
                valueFrom:
                  secretKeyRef:
                    name: blackcat-secret
                    key: git_token
          restartPolicy: OnFailure
