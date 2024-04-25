job("Parameter_Snapshot") {
	description("Copies parameters from AWS SSM Parameter Store to AWS S3.")
	keepDependencies(false)
	parameters {
		stringParam("NAMESPACE", "/namespace", "Limits the parameters fetched from AWS on a per namespace basis.")
		choiceParam("ENVIRONMENT", ["qa", "dev", "stage", "prod"], "The deployment environment of the EKS cluster.")
	}
	scm {
		git {
			remote {
				github("org_name/repo_name", "ssh")
				credentials("user_account_id")
			}
			branch("main")
		}
	}
	disabled(false)
	concurrentBuild(false)
	steps {
		shell("""#!/usr/bin/env bash +x
case \$ENVIRONMENT in
    dev)
        export AWS_ACCOUNT_ID=123456789
        export AWS_REGION=us-east-2
        export CH=de
        ;;
    stage)
        export AWS_ACCOUNT_ID=123456789
        export AWS_REGION=us-east-2
        export CH=st
        ;;
    qa)
        export AWS_ACCOUNT_ID=123456789
        export AWS_REGION=us-east-2
        export CH=qa
        ;;
    demo)
        export AWS_ACCOUNT_ID=123456789
        export AWS_REGION=us-east-2
        export CH=dm
        ;;
    prod)
        export AWS_ACCOUNT_ID=123456789
        export AWS_REGION=us-east-2
        export CH=pr
        ;;
esac

aws sts get-caller-identity
echo AssumeRole ..................................
ASSUME_ROLE_OUTPUT=\$(aws sts assume-role --role-arn "arn:aws:iam::\${AWS_ACCOUNT_ID}:role/devops-runner" --role-session-name jenkins)
export AWS_ACCESS_KEY_ID=\$(echo \$ASSUME_ROLE_OUTPUT | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=\$(echo \$ASSUME_ROLE_OUTPUT | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=\$(echo \$ASSUME_ROLE_OUTPUT | jq -r '.Credentials.SessionToken')
echo Check role ....................................
aws sts get-caller-identity

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 param_snapshot.py --namespace \${NAMESPACE} --env \${ENVIRONMENT}""")
	}
	wrappers {
		preBuildCleanup {
			deleteDirectories(false)
			cleanupParameter()
		}
	}
	configure {
		it / 'properties' / 'com.coravy.hudson.plugins.github.GithubProjectProperty' {
			'projectUrl'('https://github.com/Optm-Main/do-script-param-snapshot/')
			displayName()
		}
		it / 'properties' / 'com.sonyericsson.rebuild.RebuildSettings' {
			'autoRebuild'('false')
			'rebuildDisabled'('false')
		}
	}
}
