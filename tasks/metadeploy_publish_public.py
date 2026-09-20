"""Publish a MetaDeploy version against the public mirror repo.

MetaDeploy products are registered against the _Public mirror, because the
installer needs a public source repo. The release flow runs in the private
repo, so the stock metadeploy_publish task resolves the product by the
PRIVATE url and dies with "No product found in MetaDeploy with repo URL".

This swaps the repo identity only. The content is downloaded from GitHub
either way (metadeploy.py calls download_extract_github), so the working
directory never supplies the files.

The same swap can be done on the command line with
CUMULUSCI_AUTO_DETECT=1 CUMULUSCI_REPO_URL=<public url>, but a flow step
cannot set environment variables, and ^^task.return_value references only
resolve when they are the WHOLE option value, so the release tag cannot be
interpolated into a shell command.

Register in cumulusci.yml::

    tasks:
        metadeploy_publish_public:
            class_path: tasks.metadeploy_publish_public.PublishPublic
            options:
                public_repo_url: "https://github.com/common-unite/..._Public"
"""

from cumulusci.tasks.metadeploy import Publish
from cumulusci.utils.git import split_repo_url


class PublishPublic(Publish):
    task_docs = "Publish a MetaDeploy version, resolving the product against the public mirror repo."

    task_options = {
        **Publish.task_options,
        "public_repo_url": {
            "description": "Url of the public mirror repo the MetaDeploy product is registered against. Must match the product's repo_url exactly.",
            "required": True,
        },
    }

    def _init_task(self):
        super()._init_task()
        public_repo_url = self.options["public_repo_url"]
        owner, name = split_repo_url(public_repo_url)
        self.project_config._repo_info = dict(
            self.project_config.repo_info, owner=owner, name=name, url=public_repo_url
        )
        self.logger.info(f"Resolving the MetaDeploy product against {owner}/{name}")
