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
              - name: GIT_TOKEN
                valueFrom:
                  secretKeyRef:
                    name: blackcat-secret
                    key: git_token
          restartPolicy: OnFailure
