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
            image: blackcat
            args:
              - "python"
              - "src/main.py"
              - "--enable"
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
