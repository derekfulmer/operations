job("Manage_Route_53_Records") {
	description("CRUD job for AWS Route 53 DNS records")
	keepDependencies(false)
	parameters {
		choiceParam("ACTION", ["upsert", "delete", "read"], "The action to perform: Upsert (Creates or Updates records), Delete, and Read.")
		choiceParam("TYPE", ["A", "CNAME"], "Allows the type of record to be set: CNAME or A Record.")
		stringParam("VALUE", "none", "The value of the record to create or query, e.g. an IP address or AWS resource FQDN.")
		stringParam("NAME", "none", "The name of the to create or query. Must be a full URI, e.g. foo.bar.com.")
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
		shell("""#!/usr/bin/env bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install boto3 requests

python3 dnstruck.py --action \${ACTION} --name \${NAME} --value \${VALUE} --type \${TYPE}""")
	}
	wrappers {
		preBuildCleanup {
			deleteDirectories(false)
			cleanupParameter()
		}
	}
	configure {
		it / 'properties' / 'com.coravy.hudson.plugins.github.GithubProjectProperty' {
			'projectUrl'('https://github.com/Optm-Main/do-script-dnstruck/')
			displayName()
		}
		it / 'properties' / 'com.sonyericsson.rebuild.RebuildSettings' {
			'autoRebuild'('false')
			'rebuildDisabled'('false')
		}
	}
}
