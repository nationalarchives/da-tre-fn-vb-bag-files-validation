# da-tre-fn-vb-bag-files-validation

* [GitHub Actions](#github-actions)
* [GitHub Action Secrets](#github-action-secrets)

## GitHub Actions

| Action | Description |
| --- | --- |
| [`.github/workflows/build-deploy-and-tag-ecr-image.yml`](.github/workflows/build-deploy-and-tag-ecr-image.yml) | Gets next git version tag<br>Builds and deploys Docker image to ECR<br>If successful, tags git with new version |

## GitHub Action Secrets

Secret for main AWS authentication (using OpenID Connect):

| Name                         | Description                                               |
| ---------------------------- |-----------------------------------------------------------|
| AWS\_OPEN\_ID\_CONNECT\_ROLE\_ARN | ARN of AWS role used to authenticate GitHub with AWS |

Other secrets:

| Name                                | Description                                                                 |
| ----------------------------------- |-----------------------------------------------------------------------------|
| AWS\_CODEARTIFACT\_REPOSITORY\_NAME    | Name of AWS CodeArtifact repository to log in to for additional packages |
| AWS\_CODEARTIFACT\_REPOSITORY\_DOMAIN  | Name of AWS CodeArtifact repository's domain                             |
| AWS\_CODEARTIFACT\_REPOSITORY\_ACCOUNT | The AWS account ID that owns the CodeArtifact                            |
| AWS\_REGION                          | The AWS region to use for CodeArtifact and ECR                             |