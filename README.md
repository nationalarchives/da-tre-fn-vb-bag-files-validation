# da-tre-fn-vb-bag-files-validation

* [GitHub Actions](#github-actions)
* [GitHub Action Secrets](#github-action-secrets)

## GitHub Actions

| Action | Description |
| --- | --- |
| [`.github/workflows/build-deploy-and-tag-ecr-image.yml`](.github/workflows/build-deploy-and-tag-ecr-image.yml) | Gets next git version tag<br>Builds and deploys Docker image to ECR<br>If successful, tags git with new version |

## GitHub Action Secrets

Secret for main AWS authentication (using OpenID Connect):

| Name                         | Description                                          |
| ---------------------------- | ---------------------------------------------------- |
| AWS_OPEN_ID_CONNECT_ROLE_ARN | ARN of AWS role used to authenticate GitHub with AWS |

Other secrets:

| Name                                | Description                                                              |
| ----------------------------------- | ------------------------------------------------------------------------ |
| AWS_CODEARTIFACT_REPOSITORY_NAME    | Name of AWS CodeArtifact repository to log in to for additional packages |
| AWS_CODEARTIFACT_REPOSITORY_DOMAIN  | Name of AWS CodeArtifact repository's domain                             |
| AWS_CODEARTIFACT_REPOSITORY_ACCOUNT | The AWS account ID that owns the CodeArtifact                            |
| AWS_REGION                          | The AWS region to use for CodeArtifact and ECR                           |
